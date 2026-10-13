import {
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";

import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [token, setToken] = useState(
        localStorage.getItem("cashcowToken")
    );

    const [role, setRole] = useState(null);
    const [permissions, setPermissions] = useState([]);

    useEffect(() => {
        let cancelled = false;

        async function loadCurrentUser() {
            if (!token) {
                setRole(null);
                setPermissions([]);
                return;
            }

            try {
                const response = await api.get("/auth/me");

                if (!cancelled) {
                    setRole(response.data.role);
                    setPermissions(
                        response.data.permissions || []
                    );
                }
            } catch (error) {
                console.error(
                    "Could not load current user permissions",
                    error
                );

                if (!cancelled) {
                    setRole(null);
                    setPermissions([]);
                }
            }
        }

        loadCurrentUser();

        return () => {
            cancelled = true;
        };
    }, [token]);

    const login = (accessToken, refreshToken) => {
        localStorage.setItem(
            "cashcowToken",
            accessToken
        );

        localStorage.setItem(
            "cashcowRefreshToken",
            refreshToken
        );

        setToken(accessToken);
    };

    const logout = async () => {
        const refreshToken =
            localStorage.getItem(
                "cashcowRefreshToken"
            );

        if (refreshToken) {
            try {
                await api.post("/auth/logout", {
                    refresh_token: refreshToken,
                });
            } catch {
                // Local logout still continues.
            }
        }

        localStorage.removeItem("cashcowToken");
        localStorage.removeItem(
            "cashcowRefreshToken"
        );

        setToken(null);
        setRole(null);
        setPermissions([]);
    };

    const hasPermission = (permission) => {
        return permissions.includes(permission);
    };

    return (
        <AuthContext.Provider
            value={{
                token,
                role,
                permissions,
                hasPermission,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
