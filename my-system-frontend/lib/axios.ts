import axios from "axios";

const instance = axios.create({
  baseURL: "http://localhost:8000",
});

// interceptor για να βάζει το token σε κάθε request
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default instance;
