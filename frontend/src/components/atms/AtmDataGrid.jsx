import {
    useEffect,
    useState,
} from "react";

import {
    Box,
    Button,
    MenuItem,
    TextField,
} from "@mui/material";

import {
    DataGrid,
} from "@mui/x-data-grid";

import api from "../../api/client.js";
import { useAuth } from "../../context/AuthContext";
import RecordHistoryDialog from "../audit/RecordHistoryDialog";


const baseColumns = [
    {
        field: "id",
        headerName: "ID",
        width: 80,
    },
    {
        field: "serial_number",
        headerName: "Serial Number",
        flex: 1,
        minWidth: 150,
    },
    {
        field: "model",
        headerName: "Model",
        flex: 1,
        minWidth: 130,
    },
    {
        field: "status",
        headerName: "Status",
        flex: 1,
        minWidth: 140,
    },
    {
        field: "cash_level",
        headerName: "Cash Level",
        type: "number",
        flex: 1,
        minWidth: 110,
    },
    {
        field: "branch_id",
        headerName: "Branch ID",
        type: "number",
        flex: 1,
        minWidth: 100,
    },
];


export default function AtmDataGrid() {
    const { hasPermission } =
        useAuth();

    const [rows, setRows] =
        useState([]);

    const [rowCount, setRowCount] =
        useState(0);

    const [loading, setLoading] =
        useState(false);

    const [reloadKey, setReloadKey] =
        useState(0);

    const [historyId, setHistoryId] =
        useState(null);

    const [
        paginationModel,
        setPaginationModel,
    ] = useState({
        page: 0,
        pageSize: 5,
    });

    const [sortModel, setSortModel] =
        useState([]);

    const [search, setSearch] =
        useState("");

    const [
        debouncedSearch,
        setDebouncedSearch,
    ] = useState("");

    const [status, setStatus] =
        useState("");

    const [branchId, setBranchId] =
        useState("");

    useEffect(() => {
        const timeout = setTimeout(
            () => {
                setDebouncedSearch(
                    search
                );
            },
            350
        );

        return () =>
            clearTimeout(timeout);
    }, [search]);

    useEffect(() => {
        const loadAtms =
            async () => {
                setLoading(true);

                try {
                    const response =
                        await api.get(
                            "/atms",
                            {
                                preservePage:
                                    true,
                                params: {
                                    page:
                                        paginationModel.page +
                                        1,
                                    size:
                                        paginationModel.pageSize,
                                    sort_by:
                                        sortModel[0]
                                            ?.field ||
                                        "id",
                                    sort_dir:
                                        sortModel[0]
                                            ?.sort ||
                                        "asc",
                                    search:
                                        debouncedSearch ||
                                        undefined,
                                    status:
                                        status ||
                                        undefined,
                                    branch_id:
                                        branchId ||
                                        undefined,
                                },
                            }
                        );

                    setRows(
                        response.data
                            .items
                    );

                    setRowCount(
                        response.data
                            .total
                    );
                } finally {
                    setLoading(
                        false
                    );
                }
            };

        loadAtms();
    }, [
        paginationModel,
        sortModel,
        debouncedSearch,
        status,
        branchId,
        reloadKey,
    ]);

    const resetPage = () => {
        setPaginationModel(
            (current) => ({
                ...current,
                page: 0,
            })
        );
    };

    async function deleteAtm(id) {
        const confirmed =
            window.confirm(
                "Soft delete this ATM?"
            );

        if (!confirmed) {
            return;
        }

        await api.delete(
            `/atms/${id}`
        );

        setReloadKey(
            (value) => value + 1
        );
    }

    const columns = [
        ...baseColumns,
        {
            field: "actions",
            headerName: "Actions",
            sortable: false,
            filterable: false,
            minWidth: 190,
            renderCell: (params) => (
                <Box
                    sx={{
                        display: "flex",
                        gap: 1,
                    }}
                >
                    {hasPermission(
                        "audit:read"
                    ) && (
                        <Button
                            size="small"
                            onClick={() =>
                                setHistoryId(
                                    params.row.id
                                )
                            }
                        >
                            History
                        </Button>
                    )}

                    {hasPermission(
                        "asset:write"
                    ) && (
                        <Button
                            size="small"
                            color="error"
                            onClick={() =>
                                deleteAtm(
                                    params.row.id
                                )
                            }
                        >
                            Delete
                        </Button>
                    )}
                </Box>
            ),
        },
    ];

    return (
        <Box>
            <Box
                sx={{
                    display: "flex",
                    gap: 2,
                    mb: 2,
                    flexWrap: "wrap",
                }}
            >
                <TextField
                    label="Search model or serial"
                    size="small"
                    value={search}
                    onChange={(
                        event
                    ) => {
                        setSearch(
                            event.target
                                .value
                        );
                        resetPage();
                    }}
                />

                <TextField
                    select
                    label="Status"
                    size="small"
                    value={status}
                    sx={{
                        minWidth: 160,
                    }}
                    onChange={(
                        event
                    ) => {
                        setStatus(
                            event.target
                                .value
                        );
                        resetPage();
                    }}
                >
                    <MenuItem value="">
                        All
                    </MenuItem>

                    <MenuItem value="Operational">
                        Operational
                    </MenuItem>

                    <MenuItem value="In-Transport">
                        In-Transport
                    </MenuItem>

                    <MenuItem value="Maintenance">
                        Maintenance
                    </MenuItem>
                </TextField>

                <TextField
                    label="Branch ID"
                    size="small"
                    type="number"
                    value={branchId}
                    onChange={(
                        event
                    ) => {
                        setBranchId(
                            event.target
                                .value
                        );
                        resetPage();
                    }}
                />
            </Box>

            <Box
                sx={{
                    height: 430,
                    width: "100%",
                }}
            >
                <DataGrid
                    rows={rows}
                    columns={columns}
                    rowCount={
                        rowCount
                    }
                    loading={loading}
                    paginationMode="server"
                    sortingMode="server"
                    filterMode="server"
                    paginationModel={
                        paginationModel
                    }
                    onPaginationModelChange={
                        setPaginationModel
                    }
                    sortModel={
                        sortModel
                    }
                    onSortModelChange={(
                        model
                    ) => {
                        setSortModel(
                            model
                        );
                        resetPage();
                    }}
                    pageSizeOptions={[
                        5,
                        10,
                        25,
                        50,
                        100,
                    ]}
                    disableRowSelectionOnClick
                />
            </Box>

            <RecordHistoryDialog
                open={
                    historyId !== null
                }
                recordType="atm"
                recordId={historyId}
                onClose={() =>
                    setHistoryId(null)
                }
            />
        </Box>
    );
}
