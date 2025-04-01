import api from '../api/index'; // Importing the api instance

export const loadImageWithAuth = async (imageId) => {
  try {
    // 使用配置好的axios实例发送请求
    const response = await api.get(`/api/images/${imageId}/file/`, {
      responseType: 'blob' // 告诉axios我们期望二进制数据
    });
    
    // 创建Blob URL
    const blob = new Blob([response.data], { 
      type: response.headers['content-type'] 
    });
    return URL.createObjectURL(blob);
  } catch (error) {
    console.error(`Error loading image ${imageId}:`, error);
    return ''; // 失败时返回空字符串
  }
};


export const getMyImages = () => {
  return api.get('/api/images/my-images/'); // Adjust the endpoint as necessary
};

export const getImageUrl = (imageId) => {
  // Return URL without the token as a query parameter
  return `${api.defaults.baseURL}/api/images/${imageId}/file/`; 
};

export const loadImage = async (imageId) => {
  try {
    // Get the token
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('No access token found');
    }

    // Fetch the image with the Authorization header
    const response = await fetch(`${api.defaults.baseURL}/api/images/${imageId}/file/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to load image: ${response.status}`);
    }

    // Create Blob URL
    const blob = await response.blob();
    return URL.createObjectURL(blob);
  } catch (error) {
    console.error(`Error loading image ${imageId}:`, error);
    return ''; // Return empty string on failure
  }
};

/**
 * Upload an image to the server
 * @param {File} imageFile - The image file to upload
 * @returns {Promise} - API response with the uploaded image data
 */
export const uploadImage = (imageFile) => {
  const formData = new FormData();
  formData.append('file', imageFile);
  return api.post('/api/images/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

/**
 * Admin: Get recently verified images
 * @returns {Promise} - API response with recently verified images
 */
export const getVerifiedImages = () => {
  return api.get('/api/images/admin/images/verified/');
};

/**
 * Admin: Get all images from all users
 * @returns {Promise} - API response with all images
 */
export const getAllImages = () => {
  return api.get('/api/images/admin/images/');
};

/**
 * Admin: Delete an image
 * @param {number} imageId - The ID of the image to delete
 * @returns {Promise} - API response confirming deletion
 */
export const deleteImage = (imageId) => {
  return api.delete(`/api/images/admin/images/${imageId}/`);
};
