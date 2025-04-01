import React, { createContext, useState, useContext, useCallback } from 'react';
import api from '../api/index'; // Importing the api instance
import { 
  uploadImage as apiUploadImage,
  getMyImages as apiGetMyImages,
  getAllImages as apiGetAllImages,
  deleteImage as apiDeleteImage,
  getImageUrl as apigetImageUrl
} from '../api/images';

// Create the context
const ImageContext = createContext(null);

// Custom hook to use the image context
export const useImages = () => useContext(ImageContext);

export const ImageProvider = ({ children }) => {
  const [myImages, setMyImages] = useState([]);
  const [allImages, setAllImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Upload an image
  const uploadImage = useCallback(async (imageFile) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiUploadImage(imageFile);
      // Add the new image to the myImages array
      setMyImages(prevImages => [response.data, ...prevImages]);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Image upload failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getImageUrl = (imageId) => {
    return `${api.defaults.baseURL}/api/images/${imageId}/file/?token=${localStorage.getItem('access_token')}`;
  };
  
  // Admin: Get all images
  const getAllImages = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiGetAllImages(); 
      console.log('Response from getAllImages:', response); // Log the response
      setAllImages(Array.isArray(response.data.images) ? response.data.images : []); // Set allImages to the images array
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch all images');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // User: Get my images
  const getUserImages = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiGetMyImages();
      setMyImages(response.data);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch your images');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Admin: Delete an image
  const deleteImage = useCallback(async (imageId) => {
    setLoading(true);
    setError(null);
    try {
      await apiDeleteImage(imageId);
      // Remove the deleted image from state
      setAllImages(prevImages => prevImages.filter(img => img.id !== imageId));
      setMyImages(prevImages => prevImages.filter(img => img.id !== imageId));
      return true;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete image');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Context value
  const value = {
    myImages,
    allImages,
    loading,
    error,
    uploadImage,
    getAllImages,
    getUserImages,
    deleteImage,
    getImageUrl: apigetImageUrl
  };

  return <ImageContext.Provider value={value}>{children}</ImageContext.Provider>;
};

export default ImageContext;
