import React, { useState } from "react";
import { TextField, Button, Grid } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles((theme) => ({
  root: {
    marginTop: theme.spacing(2),    
  },
  textField: {
    flexGrow: 1,
    marginRight: theme.spacing(2),
    backgroundColor: 'white'
  },
  button: {
    padding: theme.spacing(1),
  },
}));

const ChatInput = ({ onSubmit }) => {
  const [input, setInput] = useState("");
  const classes = useStyles();

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(input);
    setInput("");
  };

  return (
    <form onSubmit={handleSubmit} className={classes.root}>
      <Grid container>
        <Grid item className={classes.textField}>
          <TextField
            value={input}
            onChange={(e) => setInput(e.target.value)}
            fullWidth
            variant="outlined"
          />
        </Grid>
        <Grid item>
          <Button variant="contained" color="primary" type="submit" className={classes.button}>
            Send
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

export default ChatInput;
