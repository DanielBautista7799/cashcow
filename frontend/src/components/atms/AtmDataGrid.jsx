import { useEffect, useState } from "react";
import {
Alert,
Box,
Button,
Chip,
CircularProgress,
Dialog,
DialogActions,
DialogContent,
DialogTitle,
MenuItem,
Stack,
TextField,
Typography,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";

import { useAuth } from "../../context/AuthContext";
import api from "../../api/client";


export default function AtmDataGrid() {
const { role } = useAuth();

const [atms, setAtms] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState("");

const [search, setSearch] = useState("");
const [statusFilter, setStatusFilter] = useState("All");

const [dialogOpen, setDialogOpen] = useState(false);

const [formValues, setFormValues] = useState({
serial_number: "",
model: "",
status: "Operational",
cash_level: "",
branch_id: "",
});

async function fetchAtms() {
try {
    setLoading(true);
    setError("");

    const response = await api.get("/atms");
    setAtms(response.data);
} catch (error) {
    console.error(error);
    setError("Unable to load ATMs.");
} finally {
    setLoading(false);
}
}

useEffect(() => {
fetchAtms();
}, []);

const handleFieldChange = (field) => (event) => {
setFormValues({
    ...formValues,
    [field]: event.target.value,
});
};

const handleSubmit = async () => {
try {
    await api.post("/atms", {
    ...formValues,
    cash_level: Number(formValues.cash_level),
    branch_id: Number(formValues.branch_id),
    });

    setDialogOpen(false);

    setFormValues({
    serial_number: "",
    model: "",
    status: "Operational",
    cash_level: "",
    branch_id: "",
    });

    await fetchAtms();
} catch (error) {
    console.error(error);
    setError("Unable to create ATM.");
}
};

const filteredAtms = atms.filter((atm) => {
const matchesSearch =
    atm.serial_number
    .toLowerCase()
    .includes(search.toLowerCase()) ||
    atm.model
    .toLowerCase()
    .includes(search.toLowerCase());

const matchesStatus =
    statusFilter === "All" ||
    atm.status === statusFilter;

return matchesSearch && matchesStatus;
});

const columns = [
{
    field: "id",
    headerName: "ID",
    width: 70,
},
{
    field: "serial_number",
    headerName: "Serial Number",
    width: 150,
},
{
    field: "model",
    headerName: "Model",
    width: 150,
},

// Color makes ATM status easy to identify
{
    field: "status",
    headerName: "Status",
    width: 150,
    renderCell: (params) => {
    let color = "default";

    if (params.value === "Operational") {
        color = "success";
    } else if (params.value === "In-Transport") {
        color = "info";
    } else if (params.value === "Maintenance") {
        color = "warning";
    } else if (params.value === "Offline") {
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

// Cash below 20% is the low-cash alert
{
    field: "cash_level",
    headerName: "Cash Level",
    width: 130,
    renderCell: (params) => (
    <Typography
        color={
        Number(params.value) < 20
            ? "error"
            : "inherit"
        }
        fontWeight={
        Number(params.value) < 20
            ? 600
            : 400
        }
    >
        {params.value}%
    </Typography>
    ),
},
{
    field: "branch_id",
    headerName: "Branch ID",
    width: 110,
},
];

if (loading) {
return <CircularProgress />;
}

return (
<Box>
    <Typography variant="h5" sx={{ mb: 2 }}>
    ATM Fleet
    </Typography>

    {error && (
    <Alert severity="error" sx={{ mb: 2 }}>
        {error}
    </Alert>
    )}

    <Stack
    direction="row"
    spacing={2}
    sx={{ mb: 2 }}
    >
    <TextField
        size="small"
        label="Search"
        value={search}
        onChange={(event) =>
        setSearch(event.target.value)
        }
    />

    <TextField
        select
        size="small"
        label="Status"
        value={statusFilter}
        onChange={(event) =>
        setStatusFilter(event.target.value)
        }
        sx={{ width: 160 }}
    >
        <MenuItem value="All">All</MenuItem>
        <MenuItem value="Operational">
        Operational
        </MenuItem>
        <MenuItem value="In-Transport">
        In-Transport
        </MenuItem>
        <MenuItem value="Maintenance">
        Maintenance
        </MenuItem>
        <MenuItem value="Offline">
        Offline
        </MenuItem>
    </TextField>

    {role === "Admin" && (
        <Button
        variant="outlined"
        onClick={() => setDialogOpen(true)}
        >
        Add ATM
        </Button>
    )}
    </Stack>

    <Box sx={{ height: 500, width: "100%" }}>
    <DataGrid
        rows={filteredAtms}
        columns={columns}
        getRowId={(row) => row.id}
    />
    </Box>

    <Dialog
    open={dialogOpen}
    onClose={() => setDialogOpen(false)}
    >
    <DialogTitle>
        Add New ATM
    </DialogTitle>

    <DialogContent>
        <Stack
        spacing={2}
        sx={{ mt: 1, minWidth: 300 }}
        >
        <TextField
            label="Serial Number"
            value={formValues.serial_number}
            onChange={handleFieldChange(
            "serial_number"
            )}
        />

        <TextField
            label="Model"
            value={formValues.model}
            onChange={handleFieldChange("model")}
        />

        <TextField
            select
            label="Status"
            value={formValues.status}
            onChange={handleFieldChange("status")}
        >
            <MenuItem value="Operational">
            Operational
            </MenuItem>

            <MenuItem value="In-Transport">
            In-Transport
            </MenuItem>

            <MenuItem value="Maintenance">
            Maintenance
            </MenuItem>

            <MenuItem value="Offline">
            Offline
            </MenuItem>
        </TextField>

        <TextField
            label="Cash Level"
            type="number"
            value={formValues.cash_level}
            onChange={handleFieldChange(
            "cash_level"
            )}
        />

        <TextField
            label="Branch ID"
            type="number"
            value={formValues.branch_id}
            onChange={handleFieldChange(
            "branch_id"
            )}
        />
        </Stack>
    </DialogContent>

    <DialogActions>
        <Button
        onClick={() =>
            setDialogOpen(false)
        }
        >
        Cancel
        </Button>

        <Button
        variant="contained"
        onClick={handleSubmit}
        >
        Create
        </Button>
    </DialogActions>
    </Dialog>
</Box>
);
}