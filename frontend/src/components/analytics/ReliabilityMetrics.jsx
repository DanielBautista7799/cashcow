import { useEffect, useState } from "react";
import { Card, CardContent, Typography, Stack } from "@mui/material";

import api from "../../api/client";


export default function ReliabilityMetrics() {
const [metrics, setMetrics] = useState([]);

useEffect(() => {
async function fetchMetrics() {
    const response = await api.get("/service-call/reliability");
    setMetrics(response.data);
}

fetchMetrics();
}, []);

return (
<Stack spacing={2}>
    {metrics.map((metric) => (
    <Card key={metric.model}>
        <CardContent>
        <Typography variant="h6">
            {metric.model}
        </Typography>

        <Typography>
            Total Service Calls: {metric.total_service_calls}
        </Typography>

        <Typography>
            Completed: {metric.service_calls_completed}
        </Typography>

        <Typography>
            Failed: {metric.service_calls_failed}
        </Typography>
        </CardContent>
    </Card>
    ))}
</Stack>
);
}