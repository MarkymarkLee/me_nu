import React, { useState, useEffect } from 'react';

interface ButtonRadioProps {
  value: string;
  label: string;
  checked: boolean;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const ButtonRadio: React.FC<ButtonRadioProps> = ({ value, label, checked, onChange }) => {
  return (
    <label style={{
      display: 'flex',
      alignItems: 'center',
      width: '100%',
      marginBottom: '8px',
    }}>
      <input
        type="radio"
        style={{ display: 'none' }}
        value={value}
        checked={checked}
        onChange={onChange}
      />
      <span style={{
        padding: '12px 16px',
        borderRadius: '10px',
        fontSize: '24px',
        width: '100%',
        height: '60px',
        textAlign: 'center',
        textAnchor: 'middle',
        justifyContent: 'center',
        alignItems: 'center',
        display: "flex",
        background: checked 
          ? 'linear-gradient(270deg, #FF6926 0%, #FFA152 100%)'
          : '#e5e7eb',
        color: checked ? 'white' : '#374151',
        cursor: 'pointer',
        transition: 'background 0.2s ease-in-out',
      }}>
        {label}
      </span>
    </label>
  );
};

interface Option {
  value: string;
  label: string;
}

interface ButtonRadioGroupProps {
    value: string | undefined;
    save_profile: (value: string) => void;
  }

const ButtonRadioGroup: React.FC<ButtonRadioGroupProps> = ({
    value,
    save_profile,
}) => {
  const [selectedValue, setSelectedValue] = useState<string>(value || '');

  useEffect(() => {
    setSelectedValue(value || '');
  }, [value]);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value;
    setSelectedValue(newValue);
    save_profile(newValue);
  };

  const options: Option[] = [
    { value: '美食評論家', label: '美食評論家' },
    { value: '朋友', label: '朋友' },
    { value: '戀人', label: '戀人' },
  ];

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
    }}>
      {options.map((option) => (
        <ButtonRadio
          key={option.value}
          value={option.value}
          label={option.label}
          checked={selectedValue === option.value}
          onChange={handleChange}
        />
      ))}
    </div>
  );
};

export default ButtonRadioGroup;
