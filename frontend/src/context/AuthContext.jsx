import { createContext, useContext, useState } from "react";
import { jwtDecode } from "jwt-decode";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
const [token, setToken] = useState(
localStorage.getItem("cashcowToken")
);

const login = (newToken) => {
localStorage.setItem("cashcowToken", newToken);
setToken(newToken);
};

const logout = () => {
localStorage.removeItem("cashcowToken");
setToken(null);
};

let role = null;

if (token) {
const decoded = jwtDecode(token);
role = decoded.role;
}

return (
<AuthContext.Provider value={{ token, role, login, logout }}>
    {children}
</AuthContext.Provider>
);
}

export function useAuth() {
return useContext(AuthContext);
}