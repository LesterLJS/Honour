import React, { useEffect, useState } from 'react';
import { useImages } from '../../context/ImageContext';
import { useAuth } from '../../context/AuthContext';
import Navbar from '../../components/common/Navbar';
import { loadImageWithAuth } from  '../../api/images';

const AdminDashboard = () => { 
  const { getAllImages, allImages, loading, error, deleteImage, getImageUrl } = useImages(); // Destructure all necessary values
  const [imageUrls, setImageUrls] = useState({});
  useEffect(() => {
    getAllImages(); // Fetch images when the component mounts
  }, [getAllImages]);
  useEffect(() => {
    const loadImageUrls = async () => {
      const urls = {};
      for (const image of allImages) {
        try {
          urls[image.id] = await loadImageWithAuth(image.id);
        } catch (error) {
          console.error(`Error loading URL for image ${image.id}:`, error);
        }
      }
      setImageUrls(urls);
    };
    
    if (allImages.length > 0) {
      loadImageUrls();
    }
  }, [allImages]);
  
  const { user } = useAuth();
  const [filters, setFilters] = useState({
    uploaded_by: '',
    deepfake_label: '',
    is_verified: ''
  });

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    });
  };

  const handleSearch = async () => {
    await getAllImages(filters);
  };

  const handleDelete = async (imageId) => {
    if (window.confirm('Are you sure you want to delete this image?')) {
      try {
        await deleteImage(imageId);
      } catch (err) {
        console.error('Failed to delete image:', err);
      }
    }
  };

  return (
    <div>
      <Navbar />
      <div className="container">
        <div className="card">
          <h2>Admin Dashboard</h2>
          <p>Welcome, {user?.username}! You have admin privileges.</p>
          <div style={{ marginTop: '15px' }}>
            <input 
              type="text" 
              name="uploaded_by" 
              placeholder="Filter by uploader" 
              value={filters.uploaded_by} 
              onChange={handleFilterChange} 
            />
            <input 
              type="text" 
              name="deepfake_label" 
              placeholder="Filter by deepfake label" 
              value={filters.deepfake_label} 
              onChange={handleFilterChange} 
            />
            <select name="is_verified" value={filters.is_verified} onChange={handleFilterChange}>
              <option value="">All</option>
              <option value="true">Verified</option>
              <option value="false">Not Verified</option>
            </select>
            <button onClick={handleSearch}>Search</button>
          </div>
        </div>
        
        <h3 style={{ marginTop: '30px' }}>All Images</h3>
        
        {loading && (
          <div className="spinner"></div>
        )}
        
        {error && (
          <div className="alert alert-danger">{error}</div>
        )}
        
        {!loading && allImages.length === 0 && (
          <div className="card">
            <p>No images found in the system.</p>
          </div>
        )}
        
        <div className="image-grid">
          {allImages.map((image) => (
            <div key={image.id} className="image-card">
              {console.log('Image ID:', image.id)} // Debugging line
              <img
                src={imageUrls[image.id] || ''} 
                alt={`ID ${image.id}`} 
                style={{ width: '100%', height: '200px', objectFit: 'cover' }} 
              />
              <div className="image-info">
                <h3>Image #{image.id}</h3>
                <p>SHA256: {image.sha256_hash.substring(0, 10)}...</p>
                <p>Uploaded by: User #{image.uploader}</p>
                <p>Uploaded: {new Date(image.uploaded_at).toLocaleString()}</p>
                <p>Deepfake: {image.deepfake_label} ({Math.round(image.deepfake_confidence * 100)}%)</p>
                <button 
                  className="btn btn-danger" 
                  onClick={() => handleDelete(image.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
