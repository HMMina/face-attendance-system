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
    // Convert UTC to Vietnam timezone (UTC+7)
    const utcDate = new Date(timestamp);
    const vietnamTime = new Date(utcDate.getTime() + (7 * 60 * 60 * 1000));
    
    return vietnamTime.toLocaleTimeString(locale, { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false
    });
  } catch (error) {
    console.error('Error formatting time:', error);
    return '';
  }
};

export const formatDateTimeFromTimestamp = (timestamp, locale = 'vi-VN') => {
  if (!timestamp) return '';
  try {
    // Convert UTC to Vietnam timezone (UTC+7)
    const utcDate = new Date(timestamp);
    const vietnamTime = new Date(utcDate.getTime() + (7 * 60 * 60 * 1000));
    
    return vietnamTime.toLocaleString(locale);
  } catch (error) {
    console.error('Error formatting datetime:', error);
    return '';
  }
};

// Format UTC time to Vietnam timezone (UTC+7)
export const formatToVietnamTime = (utcTimeString) => {
  if (!utcTimeString) return 'Chưa kết nối';
  
  try {
    // Parse UTC time and add 7 hours for Vietnam timezone
    const utcDate = new Date(utcTimeString);
    const vietnamTime = new Date(utcDate.getTime() + (7 * 60 * 60 * 1000));
    
    return vietnamTime.toLocaleString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  } catch (error) {
    console.error('Error formatting time to Vietnam timezone:', error);
    return 'Lỗi thời gian';
  }
};

export const isLateCheckIn = (timestamp, workStartHour = 8) => {
  if (!timestamp) return false;
  try {
    // Convert UTC to Vietnam timezone (UTC+7)
    const utcDate = new Date(timestamp);
    const vietnamTime = new Date(utcDate.getTime() + (7 * 60 * 60 * 1000));
    
    const workStartTime = new Date(vietnamTime);
    workStartTime.setHours(workStartHour, 0, 0, 0);
    
    return vietnamTime > workStartTime;
  } catch (error) {
    console.error('Error checking late status:', error);
    return false;
  }
};
