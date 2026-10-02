import { useState } from "react";
import {
Button,
Card,
CardContent,
Stack,
TextField,
Typography,
} from "@mui/material";

import api from "../../api/client";


export default function ReportingLines() {
const [supervisorId, setSupervisorId] = useState("");
const [result, setResult] = useState(null);

const handleSearch = async () => {
const response = await api.get("/branches/reporting-lines", {
    params: {
    supervisor_id: supervisorId,
    },
});

setResult(response.data);
};

return (
<Stack spacing={2}>
    <TextField
    label="Supervisor ID"
    type="number"
    value={supervisorId}
    onChange={(event) => setSupervisorId(event.target.value)}
    />

    <Button variant="contained" onClick={handleSearch}>
    Search
    </Button>

    {result && (
    <>
        <Typography>
        Technician Count: {result.technician_count}
        </Typography>

        {result.technicians.map((technician) => (
        <Card key={technician.technician_id}>
            <CardContent>
            <Typography variant="h6">
                {technician.technician_name}
            </Typography>

            <Typography>
                Active Service Calls:{" "}
                {technician.active_service_call_count}
            </Typography>
            </CardContent>
        </Card>
        ))}
    </>
    )}
</Stack>
);
}