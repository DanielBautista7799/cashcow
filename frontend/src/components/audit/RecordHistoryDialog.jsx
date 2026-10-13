import {
    useEffect,
    useState,
} from "react";

import {
    Alert,
    Box,
    CircularProgress,
    Dialog,
    DialogContent,
    DialogTitle,
    Divider,
    Typography,
} from "@mui/material";

import api from "../../api/client";


export default function RecordHistoryDialog({
    open,
    onClose,
    recordType,
    recordId,
}) {
    const [entries, setEntries] =
        useState([]);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");

    useEffect(() => {
        if (!open || !recordId) {
            return;
        }

        async function loadHistory() {
            setLoading(true);
            setError("");

            try {
                const url =
                    recordType === "atm"
                        ? `/atms/${recordId}/history`
                        : `/service-call/${recordId}/history`;

                const response =
                    await api.get(url);

                setEntries(
                    response.data
                );
            } catch (requestError) {
                console.error(
                    requestError
                );

                setError(
                    "Could not load history."
                );
            } finally {
                setLoading(false);
            }
        }

        loadHistory();
    }, [
        open,
        recordType,
        recordId,
    ]);

    return (
        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="md"
        >
            <DialogTitle>
                Record History
            </DialogTitle>

            <DialogContent>
                {loading && (
                    <CircularProgress />
                )}

                {error && (
                    <Alert severity="error">
                        {error}
                    </Alert>
                )}

                {!loading &&
                    !error &&
                    entries.length === 0 && (
                        <Typography>
                            No audit history yet.
                        </Typography>
                    )}

                {!loading &&
                    !error &&
                    entries.map(
                        (entry) => (
                            <Box
                                key={entry.id}
                                sx={{ py: 2 }}
                            >
                                <Typography
                                    variant="h6"
                                >
                                    {entry.action}
                                </Typography>

                                <Typography
                                    color="text.secondary"
                                >
                                    Actor:{" "}
                                    {
                                        entry.acting_username
                                    }{" "}
                                    (User{" "}
                                    {
                                        entry.acting_user_id
                                    })
                                </Typography>

                                <Typography
                                    color="text.secondary"
                                >
                                    {new Date(
                                        entry.created_at
                                    ).toLocaleString()}
                                </Typography>

                                <Box
                                    component="pre"
                                    sx={{
                                        whiteSpace:
                                            "pre-wrap",
                                        mt: 1,
                                    }}
                                >
                                    {JSON.stringify(
                                        entry.changes,
                                        null,
                                        2
                                    )}
                                </Box>

                                <Divider />
                            </Box>
                        )
                    )}
            </DialogContent>
        </Dialog>
    );
}
