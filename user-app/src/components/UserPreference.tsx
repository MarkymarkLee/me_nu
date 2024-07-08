import React, { ChangeEvent, useEffect, useState } from 'react';
import { doc, getDoc, setDoc, updateDoc } from "firebase/firestore";
import {db} from '../main';
import { Profile, UserPreferenceProps } from '../App';
import { CircularProgress, Slider } from '@material-ui/core';
import './UserPreference.css';
import ButtonRadioGroup from './RadioGroup';
import PreferenceInfo from './PreferenceInfo';
import { UserPlus } from 'lucide-react';

const UserPreference: React.FC<Profile> = ( userProfile ) => {
    const [loading, setLoading] = useState(true);
    const [userPreferences, setUserPreferences] = useState<UserPreferenceProps>(userProfile.preferences);
    const [rec_count, setRecCount] = useState<number>(userProfile.rec_count!);
    const [userCharacter, setUserCharacter] = useState<string>(userProfile.userCharacter!);

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const docRef = doc(db, "users", userProfile.userId);
                const docSnap = await getDoc(docRef);
                setLoading(false);

                if (docSnap.exists()) {
                    const userData = docSnap.data();
                    setUserPreferences(userData.preferences);
                    setRecCount(userData.rec_count);
                    setUserCharacter(userData.userCharacter);
                } else {
                    console.log("No such document!");
                }
            } catch (error) {
                console.error("Error fetching document:", error);
            }
        };

        fetchUserData();
    }, [userProfile.userId]);

    if (loading) {
        return (
            <div>
                <CircularProgress />
                <p>Loading user preferences...</p>
            </div>
        );
    }

    const marks = [
        {
            value: 1,
            label: '1',
        },
        {
            value: 2,
            label: '2',
        },
        {
            value: 3,
            label: '3',
        },
        {
            value: 4,
            label: '4',
        },
        {
            value: 5,
            label: '5',
        },
        ];

    const user_info = () => {
        return (
            <div className='profile'>
                <img className="profile_icon" src={userProfile.pictureUrl}/>
                <div className="member">
                    <div>{userProfile.displayName}</div>
                    <div className="level">v1.1blablabla</div>
                </div>
            </div>
        );
    }
    
    const bg_style = {
        width: "100%",
        height: "100%",
        alignItems: "center",
        justifyContent: "center"
    };

    const handleChange = (event: ChangeEvent<{}>, value: number | number[]) => {
        console.log(value);
        updateDoc(doc(db, "users", userProfile.userId), {
            rec_count: value
        });
    };

    const types_name = [
        "喜歡的食物",
        "不喜歡的食物",
        "不能吃的食物"
    ]

    const handleAddTag = (type: string, tag: string) => {
        let new_preferences = { ...userPreferences };
    
        if (type === "喜歡的食物") {
            new_preferences.likedFood = [...userPreferences.likedFood, tag];
        } else if (type === "不喜歡的食物") {
            new_preferences.dislikedFood = [...userPreferences.dislikedFood, tag];
        } else {
            new_preferences.cannotEatFood = [...userPreferences.cannotEatFood, tag];
        }
    
        updateDoc(doc(db, "users", userProfile.userId), {
            preferences: new_preferences
        });
    
        setUserPreferences(new_preferences);
    };
    

    const handleDeleteTag = (type: string, tag: string) => {
        console.log(tag);
        let new_preferences = { ...userPreferences };
        if (type == "喜歡的食物") {
            new_preferences.likedFood = userPreferences.likedFood.filter(item => item !== tag);
        }
        else if (type == "不喜歡的食物") {
            new_preferences.dislikedFood = userPreferences.dislikedFood.filter(item => item !== tag);
        }
        else {
            new_preferences.cannotEatFood = userPreferences.cannotEatFood.filter(item => item !== tag);
        }
        console.log(new_preferences);

        updateDoc(doc(db, "users", userProfile.userId), {
            preferences: new_preferences
        });
        setUserPreferences(new_preferences);

    };

    return (
        <div style={bg_style}>
            <div className="userInfo">
                {user_info()}
            </div>

            <div className="outLine">
                <div className="inlineBtn">
                    <PreferenceInfo main_text="喜歡的食物" food_list={userPreferences?.likedFood ?? []} icon="❤️" 
                        add_tag={handleAddTag} delete_tag={handleDeleteTag}/>
                    <PreferenceInfo main_text="不喜歡的食物" food_list={userPreferences?.dislikedFood ?? []} icon="💔" 
                        add_tag={handleAddTag} delete_tag={handleDeleteTag}/>
                    <PreferenceInfo main_text="不能吃的食物" food_list={userPreferences?.cannotEatFood ?? []} icon="🚫" 
                        add_tag={handleAddTag} delete_tag={handleDeleteTag}/>
                </div>

                <div className="inLine">
                    <span className="dot">✦</span>
                    <span className="title">每次推薦的食物數量</span>
                    <Slider
                        key={`slider-${rec_count}`}
                        defaultValue={rec_count}
                        step={1}
                        marks={marks}
                        min={1}
                        max={5}
                        style={{width: "100%"}}
                        onChangeCommitted={handleChange}
                    />
                </div>

                <div className="inLine">
                    <span className="dot">✦</span>
                    <span className="title">你的專屬機器人角色</span>
                    <ButtonRadioGroup value={userCharacter} save_profile={(value) => {
                        updateDoc(doc(db, "users", userProfile.userId), {
                            userCharacter: value
                        });
                        setUserCharacter(value);
                    }}/>
                </div>
            </div>
        </div>
    );
};

export default UserPreference;