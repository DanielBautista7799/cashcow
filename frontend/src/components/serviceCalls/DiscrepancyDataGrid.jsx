import { useEffect, useState } from "react";
import { Box, Typography } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";

import api from "../../api/client";

export default function DiscrepancyDataGrid() {
const [discrepancies, setDiscrepancies] = useState([]);

useEffect(() => {
async function fetchDiscrepancies() {
    const response = await api.get("/service-call/discrepancies");
    setDiscrepancies(response.data);
}

fetchDiscrepancies();
}, []);

const columns = [
{
    field: "service_call_id",
    headerName: "Service Call ID",
    width: 140,
},
{
    field: "title",
    headerName: "Title",
    width: 220,
},
{
    field: "atm_branch_id",
    headerName: "ATM Branch",
    width: 140,
},
{
    field: "technician_branch_id",
    headerName: "Technician Branch",
    width: 170,
},
];

return (
<Box sx={{ mt: 4 }}>
    <Typography variant="h5" sx={{ mb: 2 }}>
    Co-Location Discrepancies
    </Typography>

    <Box sx={{ height: 400, width: "100%" }}>
    <DataGrid
        rows={discrepancies}
        columns={columns}
        getRowId={(row) => row.service_call_id}
    />
    </Box>
</Box>
);
}