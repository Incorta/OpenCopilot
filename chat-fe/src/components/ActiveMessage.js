import React, { useEffect, useState, useContext } from 'react';
import DancingDots from 'components/RobotReply/DancingDots'
import ChatMsg from 'components/ChatMsg/ChatMsg';
import Grid from '@mui/material/Grid';
import { BsRobot } from 'react-icons/bs'
import { List, ListItem, ListItemIcon, ListItemText } from '@material-ui/core';
import { CheckCircle } from '@material-ui/icons';
import PendingIcon from '@mui/icons-material/Pending';
import { makeStyles } from "@material-ui/core/styles";
import LeftAlignedMessageWrapper from './RobotReply/LeftAlignedMessageWrapper';
import { SessionContext } from 'contexts/SessionProvider';

const inProgressColor = "#d39a83"
const doneColor = "DarkGreen"

const actionListUseStyles = makeStyles({
	smallIcon: {
	  fontSize: '14px !important',
	  marginRight: 8,
	  minWidth: 5,
	  color: inProgressColor,
	},
	smallText: {
	  fontSize: 14
	},
	listItem: {
	  paddingTop: 0,
	  paddingBottom: 0,
	},
	listItemIcon: {
	  marginRight: 8,  // reduce this value to decrease the space
	  minWidth: 8
	},
  });

const getAllUiCommands = (tasksList) => {
	return tasksList.filter(task => ["UiChartOp", "UiTextOp"].includes(task.operator))
}

const ActiveMessage = ({ key, message, onFinish }) => {
	const [tasks, setTasks] = useState([]);
	const { session: { sessionId } } = useContext(SessionContext);

	useEffect(() => {
		const eventSource = new EventSource(`${process.env.REACT_APP_BACKEND_URL}/async_query?chat_id=${sessionId}&query_string=${encodeURIComponent(message.text)}`);

		console.log(eventSource)

		eventSource.addEventListener('open', () => {
			console.log('SSE opened!');
		});

		eventSource.addEventListener('message', (event) => {
			console.log('SSE opened!', event);
			const tasksList = JSON.parse(event.data);
			const isAllDone = tasksList.every(task => task.status == "DONE");

			if (isAllDone) {
				eventSource.close();
				const allUiCommands = getAllUiCommands(tasksList)
				onFinish(allUiCommands, message);
				setTasks(tasksList)
			} else {
				setTasks(tasksList)
			}
		})

		eventSource.addEventListener('error', (e) => {
			console.error('Error: ',  e);
			eventSource.close();
		  });

		return () => {
			eventSource.close();
		};
	}, []);

	const actionListClasses = actionListUseStyles();

	return (
		<Grid item xs={12} container justifyContent="flex-start">
			<ChatMsg
				key={key + "_in_progress_message"}
				content={
					(<DancingDots />)
				}
			/>
			<LeftAlignedMessageWrapper>
				<List>
				{tasks.map((task) => {
					const textColor = task.status == 'DONE' ? doneColor : inProgressColor;

					return (
						<ListItem key={task.id} className={actionListClasses.listItem}>
							<ListItemIcon className={actionListClasses.listItemIcon}>
								{task.status === 'DONE' ?
								<CheckCircle className={actionListClasses.smallIcon} style={{ color: doneColor }}  /> :
								<PendingIcon className={actionListClasses.smallIcon} />}
							</ListItemIcon>
							<ListItemText primary={task.short_description} classes={{ primary: actionListClasses.smallText }}  style={{ color: textColor }} />
						</ListItem>
					)
				})}
				</List>
			</LeftAlignedMessageWrapper>
		</Grid>
	);
};

export default ActiveMessage;