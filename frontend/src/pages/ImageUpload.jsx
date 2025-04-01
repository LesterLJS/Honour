import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useImages } from '../context/ImageContext';
import Navbar from '../components/common/Navbar';
import { loadImage } from '../api/images'; // Importing loadImage function

const ImageUpload = () => {
  const { uploadImage } = useImages();
  const [files, setFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  
  const [verificationStep, setVerificationStep] = useState(0);
  const [verificationProgress, setVerificationProgress] = useState(0);
  const [similarImage, setSimilarImage] = useState(null);
 
  const navigate = useNavigate();

  // Verification steps
  const steps = [
    'SHA256 check',
    'ORB match',
    'Deepfake check',
    'blockchain storage'
  ];

  // Simulate progress during upload
  useEffect(() => {
    let interval;
    if (loading && verificationProgress < 95) {
      interval = setInterval(() => {
        setVerificationProgress((prevProgress) => {
          if (prevProgress < 20) setVerificationStep(0);
          else if (prevProgress < 40) setVerificationStep(1);
          else if (prevProgress < 60) setVerificationStep(2);
          else if (prevProgress < 80) setVerificationStep(3);
          else setVerificationStep(4);
          
          return Math.min(prevProgress + 1, 95);
        });
      }, 100);
    }
    return () => clearInterval(interval);
  }, [loading, verificationProgress]);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    
    if (selectedFiles.length === 0) {
      setFiles([]);
      setPreviews([]);
      return;
    }
    
    const nonImageFiles = selectedFiles.filter(file => !file.type.startsWith('image/'));
    if (nonImageFiles.length > 0) {
      setError('Please select only image files');
      return;
    }
    
    setFiles(selectedFiles);
    setError('');
    setSimilarImage(null);
    setVerificationStep(0);
    setVerificationProgress(0);
    
    const newPreviews = [];
    selectedFiles.forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        newPreviews.push(reader.result);
        if (newPreviews.length === selectedFiles.length) {
          setPreviews(newPreviews);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (files.length === 0) {
      setError('Please select at least one image to upload');
      return;
    }
    
    setLoading(true);
    setVerificationProgress(0);
    setSimilarImage(null);
    
    try {
      const uploadResponse = await uploadImage(files[0]);
      
      // Load the uploaded image using the loadImage function with the correct image ID
      if (!uploadResponse || !uploadResponse.id) {
        throw new Error('Upload response is undefined or does not contain data');
      }
      const imageId = uploadResponse.id; // Assuming the response contains the image ID
      const imageUrl = await loadImage(imageId);
      setPreviews([imageUrl]); // Update previews with the loaded image URL

      setSuccess('Image uploaded successfully!');
      setLoading(false);
      
      setTimeout(() => {
        navigate('/upload');
      }, 1500);
    } catch (err) {
      console.error('Upload error:', err);
      console.error('Upload response:', err.response); // Log the entire response for debugging
      setLoading(false);
      setVerificationProgress(0);
      
      if (err.response?.data?.error === 'Similar image found' || 
          err.response?.data?.error === 'Exact duplicate image found') {
        
        const errorData = err.response.data;
        setSimilarImage({
          id: errorData.image_id,
          similarity: errorData.similarity,
          stage: errorData.stage,
          message: errorData.message,
          type: errorData.duplicate_type
        });
        
        if (errorData.stage === 'sha256') setVerificationStep(0);
        else if (errorData.stage === 'orb') setVerificationStep(1);
        else if (errorData.stage === 'sift') setVerificationStep(2);
        
        setError(`Upload failed: ${errorData.message || 'Similar image found'}`);
      } else {
        setError(err.response?.data?.error || 'Failed to upload image(s)');
      }
    }
  };

  const handleViewSimilarImage = () => {
    if (similarImage && similarImage.id) {
      navigate(`/images/${similarImage.id}`);
    }
  };

  return (
    <div>
      <Navbar />
      <div className="container">
        <div className="card">
          <div style={{ marginBottom: '20px' }}></div>
          <div className="verification-steps">
            <h3>Verification Process</h3>
            <div className="steps-container">
              {steps.map((step, index) => (
                <div 
                  key={index} 
                  className={`step ${index === verificationStep && loading ? 'active' : ''} ${index < verificationStep ? 'completed' : ''}`}
                >
                  <div className="step-number">{index + 1}</div>
                  <div className="step-label">{step}</div>
                </div>
              ))}
            </div>
            {loading && (
              <div className="progress-bar-container">
                <div className="progress-bar" style={{ width: `${verificationProgress}%` }}></div>
                <div className="progress-text">{steps[verificationStep]} in progress...</div>
              </div>
            )}
          </div>
          {error && <div className="alert alert-danger">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}
          {similarImage && (
            <div className="alert alert-warning">
              <p>
                Found a {similarImage.type === 'exact' ? 'duplicate' : 'similar'} image
                {similarImage.similarity && ` (Similarity: ${(similarImage.similarity * 100).toFixed(1)}%)`}
              </p>
              <button type="button" className="btn-warning" onClick={handleViewSimilarImage}>
                View Similar Image
              </button>
            </div>
          )}
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <input
                type="file"
                id="image"
                className="form-control"
                accept="image/*"
                onChange={handleFileChange}
                disabled={loading}
              />
            </div>
            {previews.length > 0 && (
              <div style={{ marginTop: '20px', marginBottom: '20px' }}>
                <h3>Preview{previews.length > 1 ? 's' : ''}</h3>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                  {previews.map((preview, index) => (
                    <img 
                      key={index}
                      src={preview} 
                      alt={`Preview ${index + 1}`} 
                      style={{ display: 'block', borderRadius: '8px' }} 
                    />
                  ))}
                </div>
              </div>
            )}
            <button type="submit" className="btn" disabled={files.length === 0 || loading}>
              {loading ? 'Uploading...' : `Upload Image${files.length > 1 ? 's' : ''}`}
            </button>
          </form>
        </div>
        <div className="card" style={{ marginTop: '20px' }}>
          <h3>What happens when you upload?</h3>
          <ul>
            <li><strong>SHA256 Check:</strong> Verifies if the exact image already exists</li>
            <li><strong>ORB Feature Matching:</strong> Fast algorithm to detect similar images</li>
            <li><strong>SIFT Feature Matching:</strong> Precise algorithm for high-quality similarity detection</li>
            <li><strong>Deepfake Detection:</strong> Analyzes if the image has been artificially generated</li>
            <li><strong>Blockchain Storage:</strong> Creates a permanent record for verification</li>
          </ul>
        </div>
      </div>
      <style jsx="true">{`
        .verification-steps {
          margin: 20px 0;
          padding: 15px;
          background-color: #f8f9fa;
          border-radius: 8px;
        }
        .steps-container {
          display: flex;
          justify-content: space-between;
          margin-bottom: 20px;
        }
        .step {
          display: flex;
          flex-direction: column;
          align-items: center;
          width: 18%;
        }
        .step-number {
          width: 30px;
          height: 30px;
          border-radius: 50%;
          background-color: #e0e0e0;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 8px;
          font-weight: bold;
        }
        .step.active .step-number {
          background-color: #4caf50;
          color: white;
        }
        .step.completed .step-number {
          background-color: #2196f3;
          color: white;
        }
        .step-label {
          font-size: 12px;
          text-align: center;
        }
        .progress-bar-container {
          height: 10px;
          background-color: #e0e0e0;
          border-radius: 5px;
          margin-top: 10px;
          position: relative;
        }
        .progress-bar {
          height: 100%;
          background-color: #4caf50;
          border-radius: 5px;
          transition: width 0.3s ease;
        }
        .progress-text {
          text-align: center;
          margin-top: 5px;
          font-size: 12px;
          color: #666;
        }
        .btn-warning {
          background-color: #ff9800;
          color: white;
          border: none;
          padding: 5px 10px;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 10px;
        }
        .btn-warning:hover {
          background-color: #f57c00;
        }
      `}</style>
    </div>
  );
};

export default ImageUpload;
