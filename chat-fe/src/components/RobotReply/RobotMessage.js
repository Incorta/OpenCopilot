import UITextRobotAnswer from 'components/RobotReply/UITextRobotAnswer'
import UIChartRobotAnswer from 'components/RobotReply/UIChartRobotAnswer'

const Message = ({ message }) => {
    if (message.uiCommand.operator == "UiTextOp") {
        return (
            <UITextRobotAnswer data={message.uiCommand} />
        )
    } else if (message.uiCommand.operator == "UiChartOp") {
        return (
            <UIChartRobotAnswer data={message.uiCommand} />
        )
    } else {
        return (
            <div>Unknown reply {JSON.stringify(message)}</div>
        )
    }  
    
};

export default Message;