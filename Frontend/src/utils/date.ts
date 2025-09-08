import dayjs from 'dayjs';

export const getCurrentYear = (): number => {
  return dayjs().year();
};

export const generateYearOptions = (startYear?: number, endYear?: number) => {
  const start = startYear || 2000;
  const end = endYear || getCurrentYear() + 5;
  
  const years = [];
  for (let year = end; year >= start; year--) {
    years.push({ label: year.toString(), value: year });
  }
  
  return years;
};

export const formatDate = (date: string | Date, format = 'YYYY-MM-DD HH:mm'): string => {
  return dayjs(date).format(format);
};