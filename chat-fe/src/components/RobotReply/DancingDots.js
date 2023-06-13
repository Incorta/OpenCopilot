import React from 'react';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
  dot: {
    display: 'inline-block',
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    backgroundColor: 'black',
    animation: '$bounce 1.4s infinite ease-in-out both',
    '&:nth-child(1)': {
      animationDelay: '-0.32s',
    },
    '&:nth-child(2)': {
      animationDelay: '-0.16s',
    },
  },
  '@keyframes bounce': {
    '0%, 80%, 100%': {
      transform: 'scale(0)',
    },
    '40%': {
      transform: 'scale(1.0)',
    },
  },
}));

const LoadingDots = () => {
  const classes = useStyles();

  return (
    <div>
      <div className={classes.dot}></div>
      <div className={classes.dot}></div>
      <div className={classes.dot}></div>
    </div>
  );
};

export default LoadingDots;
