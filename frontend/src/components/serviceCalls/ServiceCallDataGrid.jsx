import { useEffect, useState } from "react";
import {
Alert,
Box,
Chip,
CircularProgress,
MenuItem,
Stack,
TextField,
Typography,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";

import api from "../../api/client";
import { useAuth } from "../../context/AuthContext";

export default function ServiceCallDataGrid() {
const { role } = useAuth();

const [serviceCalls, setServiceCalls] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState("");

const [search, setSearch] = useState("");
const [priorityFilter, setPriorityFilter] = useState("All");
const [statusFilter, setStatusFilter] = useState("All");

async function fetchServiceCalls() {
try {
    setLoading(true);
    setError("");

    const response = await api.get("/service-call");
    setServiceCalls(response.data);
} catch (error) {
    console.error(error);
    setError("Unable to load service calls.");
} finally {
    setLoading(false);
}
}

useEffect(() => {
fetchServiceCalls();
}, []);

const handleStatusChange = async (serviceCallId, newStatus) => {
try {
    await api.patch(`/service-call/${serviceCallId}/status`, {
    status: newStatus,
    });

    await fetchServiceCalls();
} catch (error) {
    console.error(error);
    setError("Unable to update service call.");
}
};

const filteredServiceCalls = serviceCalls.filter((serviceCall) => {
const matchesSearch = serviceCall.title
    .toLowerCase()
    .includes(search.toLowerCase());

const matchesPriority =
    priorityFilter === "All" ||
    serviceCall.priority === priorityFilter;

const matchesStatus =
    statusFilter === "All" ||
    serviceCall.status === statusFilter;

return matchesSearch && matchesPriority && matchesStatus;
});

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

// Critical calls stand out without changing any service-call logic
{
    field: "priority",
    headerName: "Priority",
    width: 120,
    renderCell: (params) => {
    let color = "success";

    if (params.value === "Medium") {
        color = "warning";
    } else if (params.value === "Critical") {
        color = "error";
    }

    return (
        <Chip
        label={params.value}
        color={color}
        size="small"
        />
    );
    },
},

// Auditor stays read-only while Admin and Technician can update status
{
    field: "status",
    headerName: "Status",
    width: 180,
    renderCell: (params) => {
    if (role === "Auditor") {
        let color = "default";

        if (params.value === "In-Progress") {
        color = "info";
        } else if (params.value === "Completed") {
        color = "success";
        } else if (params.value === "Failed") {
        color = "error";
        } else if (params.value === "Pending") {
        color = "warning";
        }

        return (
        <Chip
            label={params.value}
            color={color}
            size="small"
        />
        );
    }

    return (
        <TextField
        select
        size="small"
        value={params.value}
        onChange={(event) =>
            handleStatusChange(
            params.row.id,
            event.target.value
            )
        }
        sx={{ width: 145 }}
        >
        <MenuItem value="Pending">Pending</MenuItem>
        <MenuItem value="In-Progress">In-Progress</MenuItem>
        <MenuItem value="Completed">Completed</MenuItem>
        <MenuItem value="Failed">Failed</MenuItem>
        </TextField>
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

if (loading) {
return <CircularProgress />;
}

return (
<Box>
    <Typography variant="h5" sx={{ mb: 2 }}>
    Service Calls
    </Typography>

    {error && (
    <Alert severity="error" sx={{ mb: 2 }}>
        {error}
    </Alert>
    )}

    <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
    <TextField
        size="small"
        label="Search"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
    />

    <TextField
        select
        size="small"
        label="Priority"
        value={priorityFilter}
        onChange={(event) =>
        setPriorityFilter(event.target.value)
        }
        sx={{ width: 130 }}
    >
        <MenuItem value="All">All</MenuItem>
        <MenuItem value="Low">Low</MenuItem>
        <MenuItem value="Medium">Medium</MenuItem>
        <MenuItem value="Critical">Critical</MenuItem>
    </TextField>

    <TextField
        select
        size="small"
        label="Status"
        value={statusFilter}
        onChange={(event) =>
        setStatusFilter(event.target.value)
        }
        sx={{ width: 150 }}
    >
        <MenuItem value="All">All</MenuItem>
        <MenuItem value="Pending">Pending</MenuItem>
        <MenuItem value="In-Progress">In-Progress</MenuItem>
        <MenuItem value="Completed">Completed</MenuItem>
        <MenuItem value="Failed">Failed</MenuItem>
    </TextField>
    </Stack>

    <Box sx={{ height: 400, width: "100%" }}>
    <DataGrid
        rows={filteredServiceCalls}
        columns={columns}
        getRowId={(row) => row.id}
    />
    </Box>
</Box>
);
}