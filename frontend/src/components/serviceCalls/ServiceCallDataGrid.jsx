import { useEffect, useState } from "react";
import {
Box,
MenuItem,
Select,
Typography,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";

import api from "../../api/client";
import { useAuth } from "../../context/AuthContext";


export default function ServiceCallDataGrid() {
const [serviceCalls, setServiceCalls] = useState([]);
const { role } = useAuth();

async function fetchServiceCalls() {
const response = await api.get("/service-call");
setServiceCalls(response.data);
}

useEffect(() => {
fetchServiceCalls();
}, []);

const handleStatusChange = async (serviceCallId, newStatus) => {
await api.patch(`/service-call/${serviceCallId}/status`, {
    status: newStatus,
});

await fetchServiceCalls();
};

const columns = [
{
    field: "id",
    headerName: "ID",
    width: 70,
},
{
    field: "title",
    headerName: "Title",
    width: 220,
},
{
    field: "priority",
    headerName: "Priority",
    width: 120,
},
{
    field: "status",
    headerName: "Status",
    width: 180,
    renderCell: (params) => {
    if (role === "Auditor") {
        return params.value;
    }

    return (
        <Select
        size="small"
        value={params.value}
        onChange={(event) =>
            handleStatusChange(params.row.id, event.target.value)
        }
        >
        <MenuItem value="Pending">Pending</MenuItem>
        <MenuItem value="In-Progress">In-Progress</MenuItem>
        <MenuItem value="Completed">Completed</MenuItem>
        <MenuItem value="Failed">Failed</MenuItem>
        </Select>
    );
    },
},
{
    field: "atm_id",
    headerName: "ATM ID",
    width: 100,
},
{
    field: "technician_id",
    headerName: "Technician ID",
    width: 130,
},
];

return (
<Box sx={{ mt: 4 }}>
    <Typography variant="h5" sx={{ mb: 2 }}>
    Service Calls
    </Typography>

    <Box sx={{ height: 400, width: "100%" }}>
    <DataGrid
        rows={serviceCalls}
        columns={columns}
        getRowId={(row) => row.id}
    />
    </Box>
</Box>
);
}