import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Upload, File, X, AlertCircle, Edit, Eye, EyeOff, Save, ArrowLeft, User, CheckCircle, XCircle } from 'lucide-react';
import { categoriesApi, CategoryDetail } from '../api/categories';
import { submissionsApi } from '../api/submissions';
import { DatePickerModal } from '../components/DatePickerModal';
import { Button } from '../components/Button';
import { getReviewPeriodLabel } from '../utils/reviewPeriods';
import toast from 'react-hot-toast';
import { addDays, addMonths, addWeeks } from 'date-fns';

export const CategoryDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [category, setCategory] = useState<CategoryDetail | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [notes, setNotes] = useState('');
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [selectedDueDate, setSelectedDueDate] = useState<Date | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [users, setUsers] = useState<Array<{ id: number; username: string; email: string; first_name: string; last_name: string }>>([]);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewAction, setReviewAction] = useState<'approve' | 'reject' | null>(null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [processingReview, setProcessingReview] = useState(false);
  const [reviewingFileId, setReviewingFileId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState({
    name: '',
    description: '',
    evidence_requirements: '',
    review_period: '',
    assignee: null as number | null,
    approver: null as number | null,
  });

  useEffect(() => {
    if (id) {
      fetchCategoryDetail();
    }
    fetchUsers();
    // Load current user from localStorage
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        const userData = JSON.parse(userStr);
        setCurrentUser(userData);
      } catch (error) {
        console.error('Error parsing user from localStorage:', error);
      }
    }
  }, [id]);

  const fetchUsers = async () => {
    try {
      const usersList = await categoriesApi.getUsers();
      setUsers(usersList);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchCategoryDetail = async () => {
    if (!id) return;
    try {
      const data = await categoriesApi.getById(parseInt(id));
      setCategory(data);
      setEditForm({
        name: data.name,
        description: data.description,
        evidence_requirements: data.evidence_requirements,
        review_period: data.review_period,
        assignee: data.assignee?.id || null,
        approver: data.approver?.id || null,
      });
    } catch (error) {
      console.error('Error fetching category:', error);
      toast.error('Failed to load category details');
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = async () => {
    if (!category || !id) return;
    try {
      const updateData = {
        name: editForm.name,
        description: editForm.description,
        evidence_requirements: editForm.evidence_requirements,
        review_period: editForm.review_period,
        assignee_id: editForm.assignee,
        approver_id: editForm.approver,
      };
      await categoriesApi.update(parseInt(id), updateData);
      // Refetch to get full CategoryDetail with past_submissions
      await fetchCategoryDetail();
      setIsEditing(false);
      toast.success('Category updated successfully');
    } catch (error: any) {
      console.error('Error updating category:', error);
      toast.error(error.response?.data?.error || 'Failed to update category');
    }
  };

  const handleCancelEdit = () => {
    if (category) {
      setEditForm({
        name: category.name,
        description: category.description,
        evidence_requirements: category.evidence_requirements,
        review_period: category.review_period,
        assignee: category.assignee?.id || null,
        approver: category.approver?.id || null,
      });
    }
    setIsEditing(false);
  };

  // Hide functionality commented out
  // const handleHide = async () => {
  //   if (!category || !id) return;
  //   try {
  //     await categoriesApi.hide(parseInt(id));
  //     toast.success('Category hidden successfully');
  //     navigate('/');
  //   } catch (error: any) {
  //     console.error('Error hiding category:', error);
  //     toast.error(error.response?.data?.error || 'Failed to hide category');
  //   }
  // };

  // const handleUnhide = async () => {
  //   if (!category || !id) return;
  //   try {
  //     await categoriesApi.unhide(parseInt(id));
  //     toast.success('Category unhidden successfully');
  //     fetchCategoryDetail();
  //   } catch (error: any) {
  //     console.error('Error unhiding category:', error);
  //     toast.error(error.response?.data?.error || 'Failed to unhide category');
  //   }
  // };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(selectedFiles.filter((_, i) => i !== index));
  };

      const calculateRecommendedDate = (): Date => {
        if (!category) return new Date();
        
        const today = new Date();
        const period = category.review_period;
        
        if (period === 'DAILY') {
          return addDays(today, 1);
        } else if (period === 'DAILY_WEEKLY') {
          return addDays(today, 1); // Daily for daily/weekly
        } else if (period === 'WEEKLY') {
          return addWeeks(today, 1);
        } else if (period === 'WEEKLY_MONTHLY' || period === 'MONTHLY' || period === 'REGULAR' || period === 'REGULAR_MONTHLY') {
          return addMonths(today, 1);
        } else if (period === 'MONTHLY_QUARTERLY' || period === 'QUARTERLY') {
          return addMonths(today, 3);
        } else if (period === 'HALF_YEARLY_QUARTERLY') {
          return addMonths(today, 6);
        } else if (period === 'QUARTERLY_HALFYEARLY_ANNUALLY' || period === 'ANNUALLY') {
          return addMonths(today, 12);
        }
        return addMonths(today, 1); // Default to monthly
      };

  const handleSubmitClick = () => {
    if (!category?.current_submission) {
      toast.error('No active submission found');
      return;
    }

    if (selectedFiles.length === 0) {
      toast.error('Please select at least one file');
      return;
    }

    // Show date picker modal
    setShowDatePicker(true);
  };

  const handleDateConfirm = async (date: Date) => {
    if (!category?.current_submission) return;

    setSelectedDueDate(date);
    setUploading(true);
    try {
      await submissionsApi.submit(
        category.current_submission.id,
        selectedFiles,
        notes,
        date.toISOString().split('T')[0] // Format as YYYY-MM-DD
      );
      toast.success('Evidence submitted successfully!');
      setSelectedFiles([]);
      setNotes('');
      setSelectedDueDate(null);
      fetchCategoryDetail(); // Refresh
    } catch (error: any) {
      console.error('Error submitting:', error);
      toast.error(
        error.response?.data?.error || 'Failed to submit evidence'
      );
    } finally {
      setUploading(false);
    }
  };

  if (!category) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  // Allow uploads until the due date, regardless of submission status
  const canSubmit = (() => {
    if (!category?.current_submission) return false;
    
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Reset time to compare dates only
    const dueDate = new Date(category.current_submission.due_date);
    dueDate.setHours(0, 0, 0, 0);
    
    // Allow uploads if today is before or equal to the due date
    return today <= dueDate;
  })();

  // Check if current user is the approver
  const isApprover = currentUser && category.approver && currentUser.id === category.approver.id;

  // Check if submission can be approved/rejected
  const canReview = category.current_submission && 
    (category.current_submission.status === 'SUBMITTED' || category.current_submission.status === 'UNDER_REVIEW') &&
    isApprover;
    const handleFileApprove = (fileId: number) => {
      setReviewAction('approve');
      setReviewNotes('');
      setReviewingFileId(fileId);
      setShowReviewModal(true);
    };

    const handleFileReject = (fileId: number) => {
      setReviewAction('reject');
      setReviewNotes('');
      setReviewingFileId(fileId);
      setShowReviewModal(true);
    };

  const handleReviewSubmit = async () => {
    if (!category?.current_submission || !reviewAction) return;

    if (reviewAction === 'reject' && !reviewNotes.trim()) {
      toast.error('Review notes are required for rejection');
      return;
    }

    setProcessingReview(true);
    try {
      // Check if this is a file-level or submission-level review
      if (reviewingFileId) {
        // File-level approval/rejection
        if (reviewAction === 'approve') {
          const response = await submissionsApi.approveFile(reviewingFileId, reviewNotes);
          if (response.upload_status) {
            toast.success(response.upload_status);
          } else if (response.upload_warning) {
            toast.success('File approved successfully!', { duration: 3000 });
            toast.error(response.upload_warning, { duration: 5000 });
            if (response.upload_errors && Array.isArray(response.upload_errors)) {
              response.upload_errors.forEach((error: string) => {
                toast.error(error, { duration: 4000 });
              });
            }
          } else {
            toast.success('File approved successfully!');
          }
        } else {
          await submissionsApi.rejectFile(reviewingFileId, reviewNotes);
          toast.success('File rejected successfully!');
        }
      } else {
        // Submission-level approval/rejection
        if (reviewAction === 'approve') {
          const response = await submissionsApi.approve(category.current_submission.id, reviewNotes);
          // Check for upload status and errors in response
          if (response.upload_status) {
            toast.success(response.upload_status);
          } else if (response.upload_warning) {
            toast.success('Submission approved successfully!', { duration: 3000 });
            toast.error(response.upload_warning, { duration: 5000 });
            if (response.upload_errors && Array.isArray(response.upload_errors)) {
              response.upload_errors.forEach((error: string) => {
                toast.error(error, { duration: 4000 });
              });
            }
          } else {
            toast.success('Submission approved successfully! Files will be uploaded to Google Drive.');
          }
        } else {
          await submissionsApi.reject(category.current_submission.id, reviewNotes);
          toast.success('Submission rejected successfully!');
        }
      }
      setShowReviewModal(false);
      setReviewNotes('');
      setReviewAction(null);
      setReviewingFileId(null);
      fetchCategoryDetail(); // Refresh to get updated status
    } catch (error: any) {
      console.error('Error reviewing:', error);
      const entityType = reviewingFileId ? 'file' : 'submission';
      toast.error(error.response?.data?.error || `Failed to ${reviewAction} ${entityType}`);
    } finally {
      setProcessingReview(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            {isEditing ? (
              <div className="space-y-4">
                <div className="flex items-center gap-3 mb-4">
                  <button
                    onClick={handleCancelEdit}
                    className="text-gray-600 hover:text-gray-900"
                  >
                    <ArrowLeft size={24} />
                  </button>
                  <h2 className="text-2xl font-bold">Edit Category</h2>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category Name
                  </label>
                  <input
                    type="text"
                    value={editForm.name}
                    onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={editForm.description}
                    onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Evidence Requirements
                  </label>
                  <textarea
                    value={editForm.evidence_requirements}
                    onChange={(e) => setEditForm({ ...editForm, evidence_requirements: e.target.value })}
                    rows={5}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Review Period
                  </label>
                  <select
                    value={editForm.review_period}
                    onChange={(e) => setEditForm({ ...editForm, review_period: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="WEEKLY">Weekly</option>
                    <option value="DAILY_WEEKLY">Daily/Weekly</option>
                    <option value="WEEKLY_MONTHLY">Weekly/Monthly</option>
                    <option value="MONTHLY">Monthly</option>
                    <option value="REGULAR">Regular</option>
                    <option value="REGULAR_MONTHLY">Regular - meeting monthly</option>
                    <option value="MONTHLY_QUARTERLY">Monthly/Quarterly</option>
                    <option value="QUARTERLY">Quarterly</option>
                    <option value="HALF_YEARLY_QUARTERLY">Half yearly/Quarterly</option>
                    <option value="QUARTERLY_HALFYEARLY_ANNUALLY">Quarterly/Halfyearly/Annually</option>
                    <option value="ANNUALLY">Annually</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Assignee
                  </label>
                  <select
                    value={editForm.assignee || ''}
                    onChange={(e) => setEditForm({ ...editForm, assignee: e.target.value ? parseInt(e.target.value) : null })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Not assigned</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.first_name && user.last_name 
                          ? `${user.first_name} ${user.last_name}`.trim()
                          : user.first_name || user.last_name || user.username}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Approver
                  </label>
                  <select
                    value={editForm.approver || ''}
                    onChange={(e) => setEditForm({ ...editForm, approver: e.target.value ? parseInt(e.target.value) : null })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Not assigned</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.first_name && user.last_name 
                          ? `${user.first_name} ${user.last_name}`.trim()
                          : user.first_name || user.last_name || user.username}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex gap-2 justify-center">
                  <Button variant="secondary" onClick={handleCancelEdit}>
                    Cancel
                  </Button>
                  <Button variant="primary" onClick={handleSave}>
                    <Save size={18} className="mr-2" />
                    Save
                  </Button>
                </div>
              </div>
            ) : (
              <>
                <div className="flex items-center gap-3 mb-2">
                  <button
                    onClick={() => navigate('/')}
                    className="text-gray-600 hover:text-gray-900"
                  >
                    <ArrowLeft size={24} />
                  </button>
                  <h1 className="text-3xl font-bold">{category.name}</h1>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6"></div>
                  <p className="text-gray-600 mb-4 flex-1">{category.description}</p>
                </div>
              </>
            )}
          </div>
          {!isEditing && (
            <div className="flex items-center gap-2">
              <Button variant="primary" onClick={handleEdit}>
                <Edit size={18} className="mr-2" />
                Edit
              </Button>
              {/* Hide functionality commented out */}
              {/* {category.is_active ? (
                <Button variant="secondary" onClick={handleHide}>
                  <EyeOff size={18} className="mr-2" />
                  Hide
                </Button>
              ) : (
                <Button variant="success" onClick={handleUnhide}>
                  <Eye size={18} className="mr-2" />
                  Unhide
                </Button>
              )} */}
            </div>
          )}
        </div>

        {!isEditing && (
          <div className="space-y-4">
            {/* Other Details */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="bg-gray-50 p-3 rounded-lg">
                <span className="text-xs text-gray-500 uppercase tracking-wide block mb-1">Review Period</span>
                <p className="font-semibold text-gray-900">{getReviewPeriodLabel(category.review_period)}</p>
              </div>
              {category.current_submission && (
                <>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <span className="text-xs text-gray-500 uppercase tracking-wide block mb-1">Due Date</span>
                    <p className="font-semibold text-gray-900">
                      {new Date(
                        category.current_submission.due_date
                      ).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <span className="text-xs text-gray-500 uppercase tracking-wide block mb-1">Status</span>
                    <p className="font-semibold text-gray-900">
                      {category.current_submission.status}
                    </p>
                  </div>
                </>
              )}
              <div className="bg-gray-50 p-3 rounded-lg">
                <span className="text-xs text-gray-500 uppercase tracking-wide block mb-1">Assignee</span>
                {category.assignee ? (
                  <div className="flex items-center gap-2">
                    <User size={16} className="text-gray-400" />
                    <p className="font-semibold text-gray-900">
                      {category.assignee.first_name && category.assignee.last_name 
                        ? `${category.assignee.first_name} ${category.assignee.last_name}`.trim()
                        : category.assignee.first_name || category.assignee.last_name || category.assignee.username}
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-gray-400 italic">Not assigned</p>
                )}
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <span className="text-xs text-gray-500 uppercase tracking-wide block mb-1">Approver</span>
                {category.approver ? (
                  <div className="flex items-center gap-2">
                    <User size={16} className="text-gray-400" />
                    <p className="font-semibold text-gray-900">
                      {category.approver.first_name && category.approver.last_name 
                        ? `${category.approver.first_name} ${category.approver.last_name}`.trim()
                        : category.approver.first_name || category.approver.last_name || category.approver.username}
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-gray-400 italic">Not assigned</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Upload Section */}
      {canSubmit && !isEditing && !isApprover && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Submit Evidence</h2>

          {/* Drag and Drop Zone */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center mb-4 ${
              dragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="mx-auto mb-4 text-gray-400" size={48} />
            <p className="text-gray-600 mb-2">
              Drag and drop files here, or
            </p>
            <label className="cursor-pointer text-blue-600 hover:underline">
              <span>browse files</span>
              <input
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
              />
            </label>
          </div>

          {/* Selected Files */}
          {selectedFiles.length > 0 && (
            <div className="mb-4">
              <h3 className="font-medium mb-2">Selected Files:</h3>
              <div className="space-y-2">
                {selectedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between bg-gray-50 p-3 rounded"
                  >
                    <div className="flex items-center gap-2">
                      <File size={20} className="text-gray-400" />
                      <span className="text-sm">{file.name}</span>
                      <span className="text-xs text-gray-500">
                        ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </span>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <X size={20} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Notes */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              Notes (Optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full border border-gray-300 rounded-lg p-3 h-32"
              placeholder="Add any additional information about this submission..."
            />
          </div>

          {/* Submit Button */}
          <Button
            variant="primary"
            onClick={handleSubmitClick}
            disabled={uploading || selectedFiles.length === 0}
            className="w-full"
          >
            {uploading
              ? 'Uploading to Google Drive...'
              : 'Submit Evidence'}
          </Button>
        </div>
      )}

      {/* Date Picker Modal */}
      {showDatePicker && category && (
        <DatePickerModal
          isOpen={showDatePicker}
          onClose={() => setShowDatePicker(false)}
          onConfirm={handleDateConfirm}
          recommendedDate={calculateRecommendedDate()}
          reviewPeriod={category.review_period}
        />
      )}

      {/* Review Modal */}
      {showReviewModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-semibold mb-4">
              {reviewAction === 'approve' 
                ? (reviewingFileId ? 'Approve File' : 'Approve Submission')
                : (reviewingFileId ? 'Reject File' : 'Reject Submission')}
            </h3>
            {reviewingFileId && category?.current_submission && (
              <p className="text-sm text-gray-600 mb-4">
                File: <span className="font-medium">{category.current_submission.files.find(f => f.id === reviewingFileId)?.filename}</span>
              </p>
            )}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Review Notes {reviewAction === 'reject' && <span className="text-red-500">*</span>}
              </label>
              <textarea
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                className="w-full border border-gray-300 rounded-lg p-3 h-32 resize-none"
                placeholder={reviewAction === 'approve' 
                  ? 'Add any notes about this approval (optional)...'
                  : 'Please provide a reason for rejection (required)...'}
              />
            </div>
            <div className="flex gap-3 justify-end">
              <Button
                variant="secondary"
                onClick={() => {
                  setShowReviewModal(false);
                  setReviewNotes('');
                  setReviewAction(null);
                  setReviewingFileId(null);
                }}
                disabled={processingReview}
              >
                Cancel
              </Button>
              <Button
                variant={reviewAction === 'approve' ? 'success' : 'danger'}
                onClick={handleReviewSubmit}
                disabled={processingReview || (reviewAction === 'reject' && !reviewNotes.trim())}
              >
                {processingReview
                  ? (reviewAction === 'approve' ? 'Approving...' : 'Rejecting...')
                  : (reviewAction === 'approve' ? 'Approve' : 'Reject')}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Pending Approval Section with Submitted Files - Only visible to approvers */}
      {!isEditing && canReview && category.current_submission &&
        category.current_submission.files.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6 border-l-4 border-blue-500">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <AlertCircle className="text-blue-500" size={24} />
              Pending Approval
            </h2>
            <p className="text-gray-600 mb-4">
              This submission is awaiting your approval. Please review each file and approve or reject individually.
            </p>
            
            <div className="space-y-3">
              {category.current_submission.files.map((file) => {
                const fileStatus = (file as any).status || 'SUBMITTED';
                const canReviewFile = fileStatus === 'SUBMITTED' || fileStatus === 'UNDER_REVIEW';
                
                return (
                  <div
                    key={file.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="flex items-center gap-3 flex-1">
                      <File size={20} className="text-gray-400" />
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-gray-900">{file.filename}</span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            fileStatus === 'APPROVED' ? 'bg-green-100 text-green-800' :
                            fileStatus === 'REJECTED' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {fileStatus}
                          </span>
                        </div>
                        <span className="text-xs text-gray-500">
                          Uploaded: {new Date(file.uploaded_at).toLocaleDateString()}
                          {(file as any).reviewed_at && (
                            <> | Reviewed: {new Date((file as any).reviewed_at).toLocaleDateString()}</>
                          )}
                        </span>
                        {(file as any).submission_notes && (
                          <p className="text-xs text-gray-700 mt-1 mr-1 text-justify whitespace-pre-line">
                            <span className="font-medium">Submission Notes:</span> {(file as any).submission_notes}
                          </p>
                        )}
                        {(file as any).review_notes && (
                          <p className="text-xs text-gray-600 mt-1 italic">
                            <span className="font-medium">Review Notes:</span> {(file as any).review_notes}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <a
                        href={file.file_url || file.google_drive_file_url || '#'}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline text-sm"
                      >
                        {file.file_url ? 'View File' : 'View in Drive'}
                      </a>
                      
                      {canReviewFile && (
                        <>
                          <Button
                            variant="success"
                            onClick={() => handleFileApprove(file.id)}
                            disabled={processingReview}
                            className="ml-2"
                          >
                            <CheckCircle size={16} className="mr-1" />
                            Approve
                          </Button>
                          <Button
                            variant="danger"
                            onClick={() => handleFileReject(file.id)}
                            disabled={processingReview}
                          >
                            <XCircle size={16} className="mr-1" />
                            Reject
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

      {/* Current Submission Files - For non-approvers */}
      {!isEditing && !canReview && category.current_submission &&
        category.current_submission.files.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Submitted Files</h2>
            <div className="space-y-2">
              {category.current_submission.files.map((file) => (
                <div
                  key={file.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded"
                >
                  <div className="flex items-center gap-2 flex-1">
                    <File size={20} className="text-gray-400" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-base">{file.filename}</span>
                        <span className="text-sm text-gray-500">
                          Uploaded: {new Date(file.uploaded_at).toLocaleDateString()}
                        </span>
                      </div>
                      {(file as any).submission_notes && (
                        <p className="text-sm text-gray-700 mt-1 mr-1 text-justify whitespace-pre-line">
                          <span className="font-medium">Submission Notes:</span> {(file as any).submission_notes}
                        </p>
                      )}
                    </div>
                  </div>

                  <a
                    href={file.file_url || file.google_drive_file_url || '#'}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline text-sm"
                  >
                    {file.file_url ? 'View File' : 'View in Drive'}
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}

      {/* Submission History */}
      {!isEditing && category.past_submissions && category.past_submissions.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Submission History</h2>
          <div className="space-y-4">
            {category.past_submissions.map((submission) => (
              <div
                key={submission.id}
                className="border border-gray-200 rounded-lg p-4"
              >
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <span className="text-sm font-medium text-gray-900">
                      Period: {new Date(submission.period_start_date).toLocaleDateString()} - {new Date(submission.period_end_date).toLocaleDateString()}
                    </span>
                    {submission.submitted_by && (
                      <span className="text-xs text-gray-700 ml-2 capitalize">
                        by {submission.submitted_by.username}
                      </span>
                    )}
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    submission.status === 'APPROVED' ? 'bg-green-100 text-green-800' :
                    submission.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                    submission.status === 'SUBMITTED' ? 'bg-blue-100 text-blue-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {submission.status}
                  </span>
                </div>
                {submission.files && submission.files.length > 0 && (
                  <div className="mt-2">
                    <p className="text-base text-black mb-2">Files:</p>
                    <div className="space-y-2">
                      {submission.files.map((file) => {
                        const fileStatus = (file as any).status || 'SUBMITTED';
                        return (
                          <div key={file.id} className="pl-2 border-l-2 border-gray-200">
                            <div className="flex items-center gap-2 mb-1">
                              <a
                                href={file.file_url || file.google_drive_file_url || '#'}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-blue-600 hover:underline font-medium"
                              >
                                {file.filename}
                              </a>
                              <span className={`px-2 py-0.5 rounded-full text-sm font-medium ${
                                fileStatus === 'APPROVED' ? 'bg-green-100 text-green-800' :
                                fileStatus === 'REJECTED' ? 'bg-red-100 text-red-800' :
                                'bg-yellow-100 text-yellow-800'
                              }`}>
                                {fileStatus}
                              </span>
                            </div>
                            {(file as any).submission_notes && (
                              <div className="text-sm text-gray-600 mt-1 ml-0">
                                <span className="font-medium">Submission Notes:</span>{' '}
                                <span className="whitespace-pre-line">{((file as any).submission_notes)}</span>
                              </div>
                            )}
                            {(file as any).review_notes && (
                              <div className="text-sm text-gray-500 mt-1 ml-0">
                                <span className="font-medium">Review Notes:</span>{' '}
                                <span >{((file as any).review_notes)}</span>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
                {submission.submitted_at && (
                  <p className="text-xs text-gray-500 mt-2">
                    Submitted: {new Date(submission.submitted_at).toLocaleString()}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Comments Section */}
      {category.current_submission &&
        category.current_submission.comments.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">
              Comments & Feedback
            </h2>
            <div className="space-y-4">
              {category.current_submission.comments.map((comment, index) => (
                <div
                  key={index}
                  className="border-l-4 border-blue-500 pl-4 py-2"
                >
                  <div className="flex justify-between mb-1">
                    <span className="font-medium text-sm">
                      {comment.user.username}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(comment.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-gray-700 text-sm">{comment.comment}</p>
                </div>
              ))}
            </div>
          </div>
        )}
    </div>
  );
};

