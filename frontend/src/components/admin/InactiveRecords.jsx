import {
    useEffect,
    useState,
} from "react";

import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    CircularProgress,
    Stack,
    Typography,
} from "@mui/material";

import api from "../../api/client";
import RecordHistoryDialog from "../audit/RecordHistoryDialog";


export default function InactiveRecords() {
    const [atms, setAtms] =
        useState([]);

    const [serviceCalls, setServiceCalls] =
        useState([]);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");

    const [history, setHistory] =
        useState({
            open: false,
            type: null,
            id: null,
        });

    async function loadInactive() {
        setLoading(true);
        setError("");

        try {
            const [
                atmResponse,
                serviceCallResponse,
            ] = await Promise.all([
                api.get(
                    "/atms/inactive"
                ),
                api.get(
                    "/service-call/inactive"
                ),
            ]);

            setAtms(
                atmResponse.data
            );

            setServiceCalls(
                serviceCallResponse.data
            );
        } catch (requestError) {
            console.error(
                requestError
            );

            setError(
                "Could not load inactive records."
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadInactive();
    }, []);

    async function restoreAtm(id) {
        await api.post(
            `/atms/${id}/restore`
        );

        await loadInactive();
    }

    async function restoreServiceCall(id) {
        await api.post(
            `/service-call/${id}/restore`
        );

        await loadInactive();
    }

    if (loading) {
        return <CircularProgress />;
    }

    return (
        <Box>
            <Typography
                variant="h5"
                sx={{ mb: 1 }}
            >
                Inactive Records
            </Typography>

            <Typography
                color="text.secondary"
                sx={{ mb: 3 }}
            >
                Soft-deleted records can
                be inspected and restored.
            </Typography>

            {error && (
                <Alert
                    severity="error"
                    sx={{ mb: 2 }}
                >
                    {error}
                </Alert>
            )}

            <Typography
                variant="h6"
                sx={{ mb: 2 }}
            >
                ATMs
            </Typography>

            <Stack
                spacing={2}
                sx={{ mb: 4 }}
            >
                {atms.length === 0 && (
                    <Typography>
                        No inactive ATMs.
                    </Typography>
                )}

                {atms.map((atm) => (
                    <Card key={atm.id}>
                        <CardContent>
                            <Typography
                                variant="h6"
                            >
                                {
                                    atm.serial_number
                                }
                            </Typography>

                            <Typography>
                                {atm.model}
                            </Typography>

                            <Typography
                                color="text.secondary"
                            >
                                Deleted:{" "}
                                {atm.deleted_at
                                    ? new Date(
                                        atm.deleted_at
                                    ).toLocaleString()
                                    : "Unknown"}
                            </Typography>

                            <Typography
                                color="text.secondary"
                            >
                                Deleted by user:{" "}
                                {
                                    atm.deleted_by
                                }
                            </Typography>

                            <Stack
                                direction="row"
                                spacing={1}
                                sx={{ mt: 2 }}
                            >
                                <Button
                                    variant="contained"
                                    onClick={() =>
                                        restoreAtm(
                                            atm.id
                                        )
                                    }
                                >
                                    Restore
                                </Button>

                                <Button
                                    variant="outlined"
                                    onClick={() =>
                                        setHistory({
                                            open: true,
                                            type: "atm",
                                            id: atm.id,
                                        })
                                    }
                                >
                                    History
                                </Button>
                            </Stack>
                        </CardContent>
                    </Card>
                ))}
            </Stack>

            <Typography
                variant="h6"
                sx={{ mb: 2 }}
            >
                Service Calls
            </Typography>

            <Stack spacing={2}>
                {serviceCalls.length ===
                    0 && (
                    <Typography>
                        No inactive service
                        calls.
                    </Typography>
                )}

                {serviceCalls.map(
                    (serviceCall) => (
                        <Card
                            key={
                                serviceCall.id
                            }
                        >
                            <CardContent>
                                <Typography
                                    variant="h6"
                                >
                                    {
                                        serviceCall.title
                                    }
                                </Typography>

                                <Typography>
                                    Status:{" "}
                                    {
                                        serviceCall.status
                                    }
                                </Typography>

                                <Typography
                                    color="text.secondary"
                                >
                                    Deleted:{" "}
                                    {serviceCall.deleted_at
                                        ? new Date(
                                            serviceCall.deleted_at
                                        ).toLocaleString()
                                        : "Unknown"}
                                </Typography>

                                <Typography
                                    color="text.secondary"
                                >
                                    Deleted by
                                    user:{" "}
                                    {
                                        serviceCall.deleted_by
                                    }
                                </Typography>

                                <Stack
                                    direction="row"
                                    spacing={1}
                                    sx={{
                                        mt: 2,
                                    }}
                                >
                                    <Button
                                        variant="contained"
                                        onClick={() =>
                                            restoreServiceCall(
                                                serviceCall.id
                                            )
                                        }
                                    >
                                        Restore
                                    </Button>

                                    <Button
                                        variant="outlined"
                                        onClick={() =>
                                            setHistory({
                                                open: true,
                                                type:
                                                    "service_call",
                                                id:
                                                    serviceCall.id,
                                            })
                                        }
                                    >
                                        History
                                    </Button>
                                </Stack>
                            </CardContent>
                        </Card>
                    )
                )}
            </Stack>

            <RecordHistoryDialog
                open={history.open}
                recordType={
                    history.type
                }
                recordId={
                    history.id
                }
                onClose={() =>
                    setHistory({
                        open: false,
                        type: null,
                        id: null,
                    })
                }
            />
        </Box>
    );
}
