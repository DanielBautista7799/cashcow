import { useEffect, useState } from "react";
import {
Alert,
Card,
CardContent,
CircularProgress,
Stack,
Typography,
} from "@mui/material";

import api from "../../api/client";

export default function LowCashAlert() {
const [atms, setAtms] = useState([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
async function fetchLowCashAtms() {
    try {
    const response = await api.get("/atms", {
        params: {
        max_cash: 20,
        },
    });

    setAtms(response.data);
    } catch (error) {
    console.error(error);
    } finally {
    setLoading(false);
    }
}

fetchLowCashAtms();
}, []);

if (loading) {
return <CircularProgress />;
}

if (atms.length === 0) {
return (
    <Alert severity="success">
    No ATMs are currently below the 20% cash threshold.
    </Alert>
);
}

return (
<Stack spacing={2}>
    {atms.map((atm) => (
    <Card
        key={atm.id}
        sx={{
        borderLeft: 4,
        borderColor: "error.main",
        }}
    >
        <CardContent>
        <Typography variant="h6">
            {atm.serial_number}
        </Typography>

        <Typography>
            Model: {atm.model}
        </Typography>

        {/* Low cash is the important value, so it is highlighted */}
        <Typography
            color="error"
            fontWeight={600}
        >
            Cash Level: {atm.cash_level}%
        </Typography>

        <Typography>
            Branch ID: {atm.branch_id}
        </Typography>
        </CardContent>
    </Card>
    ))}
</Stack>
);
}