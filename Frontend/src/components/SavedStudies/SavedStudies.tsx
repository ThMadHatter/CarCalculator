import React, { useState, useEffect } from 'react';
import { Card, List, Button, Popconfirm, Input, Modal, message, Space, Tag } from 'antd';
import { SaveOutlined, DeleteOutlined, DownloadOutlined, UploadOutlined } from '@ant-design/icons';
import { SavedStudy, EstimateRequest } from '../../types/api';
import { getSavedStudies, saveStudy, deleteStudy } from '../../utils/storage';
import { formatDate } from '../../utils/date';

interface SavedStudiesProps {
  currentData?: EstimateRequest;
  onLoadStudy: (data: EstimateRequest) => void;
}

const SavedStudies: React.FC<SavedStudiesProps> = ({ currentData, onLoadStudy }) => {
  const [studies, setStudies] = useState<SavedStudy[]>([]);
  const [saveModalVisible, setSaveModalVisible] = useState(false);
  const [studyName, setStudyName] = useState('');

  useEffect(() => {
    loadStudies();
  }, []);

  const loadStudies = () => {
    const savedStudies = getSavedStudies();
    setStudies(savedStudies);
  };

  const handleSave = async () => {
    if (!currentData || !studyName.trim()) {
      message.error('Please enter a name for the study');
      return;
    }

    try {
      await saveStudy(studyName.trim(), currentData);
      message.success('Study saved successfully');
      setSaveModalVisible(false);
      setStudyName('');
      loadStudies();
    } catch (error) {
      message.error('Failed to save study');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      deleteStudy(id);
      message.success('Study deleted');
      loadStudies();
    } catch (error) {
      message.error('Failed to delete study');
    }
  };

  const handleLoad = (study: SavedStudy) => {
    onLoadStudy(study.data);
    message.success(`Loaded study: ${study.name}`);
  };

  const handleExport = () => {
    const dataStr = JSON.stringify(studies, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `car-studies-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    message.success('Studies exported successfully');
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const importedStudies = JSON.parse(e.target?.result as string);
            if (Array.isArray(importedStudies)) {
              localStorage.setItem('car_estimator_studies', JSON.stringify(importedStudies));
              loadStudies();
              message.success(`Imported ${importedStudies.length} studies`);
            } else {
              message.error('Invalid file format');
            }
          } catch (error) {
            message.error('Failed to import studies');
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  return (
    <Card
      title="Saved Studies"
      size="small"
      extra={
        <Space>
          <Button 
            type="primary" 
            icon={<SaveOutlined />} 
            size="small"
            onClick={() => setSaveModalVisible(true)}
            disabled={!currentData}
          >
            Save
          </Button>
          <Button 
            icon={<DownloadOutlined />} 
            size="small"
            onClick={handleExport}
            disabled={studies.length === 0}
          >
            Export
          </Button>
          <Button 
            icon={<UploadOutlined />} 
            size="small"
            onClick={handleImport}
          >
            Import
          </Button>
        </Space>
      }
      style={{ marginBottom: 16 }}
    >
      {studies.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#666', padding: '20px 0' }}>
          No saved studies yet. Create an estimate and save it for later reference.
        </div>
      ) : (
        <List
          size="small"
          dataSource={studies}
          renderItem={(study) => (
            <List.Item
              actions={[
                <Button
                  type="link"
                  size="small"
                  onClick={() => handleLoad(study)}
                >
                  Load
                </Button>,
                <Popconfirm
                  title="Are you sure you want to delete this study?"
                  onConfirm={() => handleDelete(study.id)}
                  okText="Yes"
                  cancelText="No"
                >
                  <Button
                    type="link"
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                  />
                </Popconfirm>
              ]}
            >
              <List.Item.Meta
                title={study.name}
                description={
                  <Space>
                    <Tag color="blue">{study.data.brand}</Tag>
                    <Tag color="green">{study.data.model}</Tag>
                    <span style={{ color: '#666', fontSize: '12px' }}>
                      {formatDate(study.createdAt)}
                    </span>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      )}

      <Modal
        title="Save Current Study"
        open={saveModalVisible}
        onOk={handleSave}
        onCancel={() => {
          setSaveModalVisible(false);
          setStudyName('');
        }}
        okText="Save"
        cancelText="Cancel"
      >
        <Input
          placeholder="Enter a name for this study..."
          value={studyName}
          onChange={(e) => setStudyName(e.target.value)}
          onPressEnter={handleSave}
          maxLength={50}
        />
      </Modal>
    </Card>
  );
};

export default SavedStudies;