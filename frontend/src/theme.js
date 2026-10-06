import { createTheme } from "@mui/material";

const theme = createTheme({
palette: {
primary: {
    main: "#3F7467",
},

background: {
    default: "#F6F3EC",
    paper: "#FFFFFF",
},

text: {
    primary: "#26352F",
    secondary: "#68756F",
},

success: {
    main: "#4F8A6F",
},

warning: {
    main: "#D29A43",
},

error: {
    main: "#C95C5C",
},

info: {
    main: "#6591A6",
},
},

shape: {
borderRadius: 10,
},
});

export default theme;