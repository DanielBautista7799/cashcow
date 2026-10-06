import { useState } from "react";
import { Alert, Box, Button, TextField, Typography } from "@mui/material";

import api from "../../api/client";
import { useAuth } from "../../context/AuthContext";

export default function Login() {
    const { login } = useAuth();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = async (event) => {
        event.preventDefault();
        setError("");

        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        try {
            const response = await api.post("/auth/token", formData, {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            });

            login(response.data.access_token);
        } catch (err) {
            if (err.response?.status === 401) {
                setError("Incorrect Username or password");
            } else {
                setError("Something went wrong logging in, please try again shortly");
            }
        }
    };

    return (
        <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{ maxWidth: 400, mx: "auto", mt: 8 }}
        >
            <Typography variant="h4" sx={{ mb: 2 }}>
                CashCow Login
            </Typography>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            <TextField
                fullWidth
                label="Username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                sx={{ mb: 2 }}
            />

            <TextField
                fullWidth
                label="Password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                sx={{ mb: 2 }}
            />

            <Button type="submit" variant="contained" fullWidth>
                Login
            </Button>
        </Box>
    );
}