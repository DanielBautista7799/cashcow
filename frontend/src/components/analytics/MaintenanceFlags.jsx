import { useEffect, useState } from "react";
import {
Alert,
Card,
CardContent,
Chip,
CircularProgress,
Stack,
Typography,
} from "@mui/material";

import api from "../../api/client";

export default function MaintenanceFlags() {
const [flags, setFlags] = useState([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
async function fetchMaintenanceFlags() {
    try {
    const response = await api.get(
        "/branches/maintenance-flags"
    );

    setFlags(response.data);
    } catch (error) {
    console.error(error);
    } finally {
    setLoading(false);
    }
}

fetchMaintenanceFlags();
}, []);

if (loading) {
return <CircularProgress />;
}

if (flags.length === 0) {
return (
    <Alert severity="success">
    No branches are above the 30% maintenance threshold.
    </Alert>
);
}

return (
<Stack spacing={2}>
    {flags.map((flag) => (
    <Card
        key={flag.branch_id}
        sx={{
        borderLeft: 4,
        borderColor: "warning.main",
        }}
    >
        <CardContent>
        <Typography variant="h6">
            {flag.branch_name}
        </Typography>

        {/* Makes the maintenance percentage easy to notice */}
        <Chip
            label={`${Number(
            flag.maintenance_percentage
            ).toFixed(1)}% Maintenance`}
            color="warning"
            size="small"
            sx={{ my: 1 }}
        />

        <Typography>
            Total ATMs: {flag.total_atms}
        </Typography>

        <Typography>
            ATMs in Maintenance: {flag.maintenance_count}
        </Typography>
        </CardContent>
    </Card>
    ))}
</Stack>
);
}