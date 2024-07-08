import React, { useState, useRef, useEffect } from 'react';
import { Chip} from '@material-ui/core';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import IconButton from '@material-ui/core/IconButton';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';

interface FoodTagProps {
  food: string;
  delete_tag: () => void;
}

const FoodTag: React.FC<FoodTagProps> = ({ food, delete_tag }) => (
  <Chip label={food} onDelete={delete_tag} style={{ margin: '2px' }} />
);

interface PreferenceInfoProps {
  main_text: string;
  food_list: string[];
  icon: string;
  add_tag: (type:string, tag:string) => void;
  delete_tag: (type:string, tag:string) => void;
}

const PreferenceInfo: React.FC<PreferenceInfoProps> = ({ main_text, food_list, icon , add_tag, delete_tag}) => {
  const [expanded, setExpanded] = useState(false);
  const [visibleTags, setVisibleTags] = useState<string[]>([]);
  const [open, setOpen] = React.useState(false);

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  useEffect(() => {
    if (expanded) {
      setVisibleTags(food_list);
      return;
    }

    setVisibleTags(food_list.slice(0, 5));
    
  }, [food_list, expanded]);

  const toggleExpand = () => {
    setExpanded(!expanded);
  };

  return (
    <div className="preference_info">
        <div style={
          {
            display: 'flex',
            alignItems: 'center',
            padding: '10px',
          }
        }>
          <span className="icon">{icon}</span>
          <span className="title">{main_text}</span>
          <span style={{flex: 1}}></span>
          <IconButton
            onClick={() => {
              handleClickOpen();
            }}
            color='primary'
            >
            <AddCircleIcon />
          </IconButton>
        </div>
        
        <div className="tag_section">
            {
                visibleTags.map((food, index) => (
                    <FoodTag key={index} food={food} delete_tag={()=>{
                      delete_tag(main_text, food);
                    }} />
                ))
            }
            { food_list.length > 5 &&
            <Chip
                label={expanded ? "顯示更少" : "更多..."}
                onClick={toggleExpand}
                color="secondary"
                variant="outlined"
                style={{ margin: '2px' }}
            />
            }
        </div>

        <React.Fragment>
          <Dialog
            open={open}
            onClose={handleClose}
            PaperProps={{
              component: 'form',
              onSubmit: (event: React.FormEvent<HTMLDivElement>) => {
                event.preventDefault();
                const formData = new FormData(event.currentTarget as unknown as HTMLFormElement);
                const formJson = Object.fromEntries((formData as any).entries());
                const food = formJson.name;
                add_tag(main_text, food);
                handleClose();
              },
            }}
          >
            <DialogTitle>
              {
                main_text === "喜歡的食物" ? "新增喜歡的食物" : 
                main_text === "不喜歡的食物" ? "新增不喜歡的食物" : "新增不能吃的食物"
              }
            </DialogTitle>
            <DialogContent>
              <TextField
                autoFocus
                required
                margin="dense"
                id="name"
                name="name"
                label="食物名稱"
                fullWidth
                variant="standard"
              />
            </DialogContent>
            <DialogActions>
              <Button onClick={handleClose}>取消</Button>
              <Button type="submit">送出</Button>
            </DialogActions>
          </Dialog>
        </React.Fragment>
    </div>
  );
};

export default PreferenceInfo;