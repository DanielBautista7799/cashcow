import { useEffect, useState } from "react";
import {
Card,
CardContent,
Chip,
CircularProgress,
Stack,
Typography,
} from "@mui/material";

import api from "../../api/client";

export default function ReliabilityMetrics() {
const [metrics, setMetrics] = useState([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
async function fetchReliabilityMetrics() {
    try {
    const response = await api.get(
        "/service-call/reliability"
    );

    setMetrics(response.data);
    } catch (error) {
    console.error(error);
    } finally {
    setLoading(false);
    }
}

fetchReliabilityMetrics();
}, []);

if (loading) {
return <CircularProgress />;
}

return (
<Stack spacing={2}>
    {metrics.map((metric) => (
    <Card key={metric.model}>
        <CardContent>
        <Typography variant="h6">
            {metric.model}
        </Typography>

        <Typography sx={{ mb: 1 }}>
            Total Service Calls: {metric.total_service_calls}
        </Typography>

        {/* Colors make successful and failed outcomes easier to compare */}
        <Stack direction="row" spacing={1}>
            <Chip
            label={`${metric.service_calls_completed} Completed`}
            color="success"
            size="small"
            />

            <Chip
            label={`${metric.service_calls_failed} Failed`}
            color={
                metric.service_calls_failed > 0
                ? "error"
                : "default"
            }
            size="small"
            />
        </Stack>
        </CardContent>
    </Card>
    ))}
</Stack>
);
}