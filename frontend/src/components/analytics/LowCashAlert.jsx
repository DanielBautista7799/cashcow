import { useEffect, useState } from "react";
import { Card, CardContent, Stack, Typography } from "@mui/material";

import api from "../../api/client";


export default function LowCashAlert() {
const [atms, setAtms] = useState([]);

useEffect(() => {
async function fetchLowCashAtms() {
    const response = await api.get("/atms", {
    params: {
        max_cash: 20,
    },
    });

    setAtms(response.data);
}

fetchLowCashAtms();
}, []);

return (
<Stack spacing={2}>
    {atms.map((atm) => (
    <Card key={atm.id}>
        <CardContent>
        <Typography variant="h6">
            {atm.serial_number}
        </Typography>

        <Typography>
            Model: {atm.model}
        </Typography>

        <Typography>
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