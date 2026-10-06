import { useEffect, useState } from "react";
import {
Alert,
Box,
Chip,
CircularProgress,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";

import api from "../../api/client";


export default function DiscrepancyDataGrid() {
const [discrepancies, setDiscrepancies] = useState([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
async function fetchDiscrepancies() {
    try {
    const response = await api.get(
        "/service-call/discrepancies"
    );

    setDiscrepancies(response.data);
    } catch (error) {
    console.error(error);
    } finally {
    setLoading(false);
    }
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
    width: 250,
},
{
    field: "atm_branch_id",
    headerName: "ATM Branch ID",
    width: 140,
},
{
    field: "technician_branch_id",
    headerName: "Technician Branch ID",
    width: 170,
},

// Every row here represents a branch mismatch
{
    field: "issue",
    headerName: "Issue",
    width: 130,
    sortable: false,
    renderCell: () => (
    <Chip
        label="Mismatch"
        color="warning"
        size="small"
    />
    ),
},
];

if (loading) {
return <CircularProgress />;
}

if (discrepancies.length === 0) {
return (
    <Alert severity="success">
    No co-location discrepancies found.
    </Alert>
);
}

return (
<Box sx={{ height: 350, width: "100%" }}>
    <DataGrid
    rows={discrepancies}
    columns={columns}
    getRowId={(row) => row.service_call_id}
    />
</Box>
);
}