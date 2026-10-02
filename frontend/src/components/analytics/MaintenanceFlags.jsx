import { useEffect, useState } from "react";
import { Card, CardContent, Typography, Stack } from "@mui/material";

import api from "../../api/client";


export default function MaintenanceFlags() {
const [branches, setBranches] = useState([]);

useEffect(() => {
async function fetchFlags() {
    const response = await api.get("/branches/maintenance-flags");
    setBranches(response.data);
}

fetchFlags();
}, []);

return (
<Stack spacing={2}>
    {branches.map((branch) => (
    <Card key={branch.branch_id}>
        <CardContent>
        <Typography variant="h6">
            {branch.branch_name}
        </Typography>

        <Typography>
            Total ATMs: {branch.total_atms}
        </Typography>

        <Typography>
            Maintenance: {branch.maintenance_count}
        </Typography>

        <Typography>
            Maintenance Percentage: {branch.maintenance_percentage}%
        </Typography>
        </CardContent>
    </Card>
    ))}
</Stack>
);
}