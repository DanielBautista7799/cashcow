import { useEffect, useState } from "react";

import {
    Alert,
    Box,
    Card,
    CardContent,
    Chip,
    CircularProgress,
    Stack,
    Typography,
} from "@mui/material";

import api from "../../api/client";

export default function RolePermissions() {
    const [roles, setRoles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function loadRoles() {
            try {
                const response =
                    await api.get("/auth/roles");

                setRoles(response.data);
            } catch (requestError) {
                console.error(requestError);

                setError(
                    "Could not load role permissions."
                );
            } finally {
                setLoading(false);
            }
        }

        loadRoles();
    }, []);

    if (loading) {
        return <CircularProgress />;
    }

    if (error) {
        return (
            <Alert severity="error">
                {error}
            </Alert>
        );
    }

    return (
        <Box>
            <Typography
                variant="h5"
                sx={{ mb: 1 }}
            >
                Role Permissions
            </Typography>

            <Typography
                color="text.secondary"
                sx={{ mb: 3 }}
            >
                Permissions assigned to each
                CashCow role.
            </Typography>

            <Stack spacing={2}>
                {roles.map((role) => (
                    <Card key={role.role}>
                        <CardContent>
                            <Typography
                                variant="h6"
                                sx={{ mb: 2 }}
                            >
                                {role.role}
                            </Typography>

                            <Stack
                                direction="row"
                                spacing={1}
                                useFlexGap
                                flexWrap="wrap"
                            >
                                {role.permissions.map(
                                    (permission) => (
                                        <Chip
                                            key={
                                                permission
                                            }
                                            label={
                                                permission
                                            }
                                            variant="outlined"
                                        />
                                    )
                                )}
                            </Stack>
                        </CardContent>
                    </Card>
                ))}
            </Stack>
        </Box>
    );
}
