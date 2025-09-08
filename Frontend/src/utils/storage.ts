import { SavedStudy, EstimateRequest } from '../types/api';

const STORAGE_KEY = 'car_estimator_studies';

export const getSavedStudies = (): SavedStudy[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Error loading saved studies:', error);
    return [];
  }
};

export const saveStudy = (name: string, data: EstimateRequest): SavedStudy => {
  const study: SavedStudy = {
    id: Date.now().toString(),
    name,
    data,
    createdAt: new Date().toISOString(),
  };

  try {
    const studies = getSavedStudies();
    const updatedStudies = [study, ...studies.slice(0, 9)]; // Keep only 10 most recent
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedStudies));
    return study;
  } catch (error) {
    console.error('Error saving study:', error);
    throw new Error('Failed to save study');
  }
};

export const deleteStudy = (id: string): void => {
  try {
    const studies = getSavedStudies();
    const filtered = studies.filter(study => study.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
  } catch (error) {
    console.error('Error deleting study:', error);
    throw new Error('Failed to delete study');
  }
};