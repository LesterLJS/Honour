import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';


const root = ReactDOM.createRoot(document.getElementById('root'));

// 在开发环境中禁用StrictMode以避免双重渲染问题
// 在生产环境中可以考虑重新启用
root.render(
  <App />
);
