// Date utility functions for consistent date handling
export const getCurrentDateString = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = (now.getMonth() + 1).toString().padStart(2, '0');
  const day = now.getDate().toString().padStart(2, '0');
  return `${year}-${month}-${day}`;
};

export const formatDateFromTimestamp = (timestamp) => {
  if (!timestamp) return '';
  return timestamp.split('T')[0];
};

export const formatTimeFromTimestamp = (timestamp, locale = 'vi-VN') => {
  if (!timestamp) return '';
  try {
    return new Date(timestamp).toLocaleTimeString(locale, { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  } catch (error) {
    console.error('Error formatting time:', error);
    return '';
  }
};

export const formatDateTimeFromTimestamp = (timestamp, locale = 'vi-VN') => {
  if (!timestamp) return '';
  try {
    return new Date(timestamp).toLocaleString(locale);
  } catch (error) {
    console.error('Error formatting datetime:', error);
    return '';
  }
};

export const isLateCheckIn = (timestamp, workStartHour = 8) => {
  if (!timestamp) return false;
  try {
    const checkInTime = new Date(timestamp);
    const workStartTime = new Date(checkInTime);
    workStartTime.setHours(workStartHour, 0, 0, 0);
    return checkInTime > workStartTime;
  } catch (error) {
    console.error('Error checking late status:', error);
    return false;
  }
};
