// import axios from "axios";

// const api = axios.create({
//   baseURL: `${import.meta.env.VITE_API_BASE_URL ?? ""}/api/v1`,
//   headers: {
//     "Content-Type": "application/json",
//   },
// });

// api.interceptors.response.use(
//   (response) => response,
//   (error) => {
//     const message =
//       error.response?.data?.detail ?? error.message ?? "Unexpected error";
//     return Promise.reject(new Error(message));
//   },
// );

// export default api;

import axios from "axios";

const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_BASE_URL ?? ""}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  console.log("[API Request Interceptor] token exists:", !!token);

  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`);
    console.log("[API Request Interceptor] headers after set:", {
      authorization: config.headers.get("authorization"),
      Authorization: config.headers.get("Authorization"),
    });
  }
  console.log(
    "[API Request Interceptor] final config headers:",
    Object.fromEntries(config.headers),
  );
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ?? error.message ?? "Unexpected error";
    return Promise.reject(new Error(message));
  },
);

export default api;
