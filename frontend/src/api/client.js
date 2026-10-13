import axios from "axios";

const baseURL =
    import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const api = axios.create({
    baseURL,
});

let refreshPromise = null;

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("cashcowToken");

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

api.interceptors.response.use(
    (response) => {
        if (
            response.data &&
            Array.isArray(response.data.items) &&
            typeof response.data.total === "number" &&
            !response.config.preservePage
        ) {
            response.data = response.data.items;
        }

        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        if (
            error.response?.status !== 401 ||
            originalRequest?._retry ||
            originalRequest?.url === "/auth/token" ||
            originalRequest?.url === "/auth/refresh"
        ) {
            return Promise.reject(error);
        }

        const refreshToken =
            localStorage.getItem("cashcowRefreshToken");

        if (!refreshToken) {
            localStorage.removeItem("cashcowToken");
            localStorage.removeItem("cashcowRefreshToken");
            window.location.href = "/";
            return Promise.reject(error);
        }

        originalRequest._retry = true;

        if (!refreshPromise) {
            refreshPromise = axios
                .post(`${baseURL}/auth/refresh`, {
                    refresh_token: refreshToken,
                })
                .then((response) => {
                    localStorage.setItem(
                        "cashcowToken",
                        response.data.access_token
                    );

                    localStorage.setItem(
                        "cashcowRefreshToken",
                        response.data.refresh_token
                    );

                    return response.data.access_token;
                })
                .finally(() => {
                    refreshPromise = null;
                });
        }

        try {
            const newAccessToken = await refreshPromise;

            originalRequest.headers.Authorization =
                `Bearer ${newAccessToken}`;

            return api(originalRequest);
        } catch (refreshError) {
            localStorage.removeItem("cashcowToken");
            localStorage.removeItem("cashcowRefreshToken");
            window.location.href = "/";
            return Promise.reject(refreshError);
        }
    }
);

export default api;
