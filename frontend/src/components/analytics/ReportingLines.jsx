import { useState } from "react";
import {
Alert,
Button,
Card,
CardContent,
Chip,
CircularProgress,
Stack,
TextField,
Typography,
} from "@mui/material";

import api from "../../api/client";

export default function ReportingLines() {
const [supervisorId, setSupervisorId] = useState("");
const [result, setResult] = useState(null);
const [loading, setLoading] = useState(false);

async function fetchReportingLines() {
if (!supervisorId) {
    return;
}

try {
    setLoading(true);

    const response = await api.get(
    "/branches/reporting-lines",
    {
        params: {
        supervisor_id: Number(supervisorId),
        },
    }
    );

    setResult(response.data);
} catch (error) {
    console.error(error);
} finally {
    setLoading(false);
}
}

return (
<Stack spacing={2}>
    <Stack direction="row" spacing={2}>
    <TextField
        size="small"
        type="number"
        label="Supervisor ID"
        value={supervisorId}
        onChange={(event) =>
        setSupervisorId(event.target.value)
        }
    />

    <Button
        variant="outlined"
        onClick={fetchReportingLines}
    >
        Search
    </Button>
    </Stack>

    {loading && <CircularProgress />}

    {result && !loading && (
    <>
        <Alert severity="info">
        Supervisor {result.supervisor_id} has{" "}
        {result.technician_count} reporting technicians.
        </Alert>

        {result.technicians.map((technician) => (
        <Card key={technician.technician_id}>
            <CardContent>
            <Typography variant="h6">
                {technician.technician_name}
            </Typography>

            <Typography>
                Technician ID: {technician.technician_id}
            </Typography>

            {/* Active work is highlighted without changing the returned data */}
            <Chip
                label={`${technician.active_service_call_count} Active Service Calls`}
                color={
                technician.active_service_call_count > 0
                    ? "warning"
                    : "success"
                }
                size="small"
                sx={{ mt: 1 }}
            />
            </CardContent>
        </Card>
        ))}
    </>
    )}
</Stack>
);
}