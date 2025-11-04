import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import '../../services/document_service.dart';

class DocumentUploadStep extends StatefulWidget {
  final VoidCallback? onCompleted;
  final String? authToken;
  final int? userId;

  const DocumentUploadStep({
    Key? key,
    this.onCompleted,
    this.authToken,
    this.userId,
  }) : super(key: key);

  @override
  State<DocumentUploadStep> createState() => _DocumentUploadStepState();
}

class _DocumentUploadStepState extends State<DocumentUploadStep> {
  final DocumentService _documentService = DocumentService();

  // Document upload states - simplified to transcripts only
  final Map<String, DocumentUploadState> _uploadStates = {
    'transcript': DocumentUploadState(),
  };

  // Document type configurations - simplified to transcripts only
  final Map<String, DocumentTypeConfig> _documentTypes = {
    'transcript': DocumentTypeConfig(
      title: 'Academic Transcript',
      description: 'Upload your official academic transcript (high school, college, or trade school)',
      icon: Icons.school_outlined,
    ),
  };

  @override
  void initState() {
    super.initState();
    if (widget.authToken != null) {
      _documentService.setAuthToken(widget.authToken!);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.colorScheme.background,
      appBar: AppBar(
        title: Text('Upload Documents'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: theme.colorScheme.onBackground,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Logo and title
              Image.asset('assets/images/aada_logo_login.png', height: 80),
              SizedBox(height: 16),
              Text(
                'Upload Documents',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.amber,
                ),
              ),
              SizedBox(height: 8),
              Text(
                'Step 3 of 4: Upload Required Documents',
                style: TextStyle(
                  fontSize: 16,
                  color: theme.colorScheme.onBackground.withOpacity(0.7),
                ),
              ),
              SizedBox(height: 32),

              // Progress indicator
              _ProgressIndicator(currentStep: 3, totalSteps: 4),
              SizedBox(height: 32),

              const Text(
                'Please upload the following documents to complete your registration. All documents will be reviewed for verification.',
                style: TextStyle(fontSize: 16, color: Colors.grey),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),

            // Document upload cards
            ..._documentTypes.entries.map((entry) {
              return _buildDocumentUploadCard(entry.key, entry.value);
            }).toList(),

            const SizedBox(height: 32),

            // Complete button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _canComplete() ? _completeOnboarding : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _canComplete() ? Colors.amber : Colors.grey,
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'Next Step',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
              ),
            ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDocumentUploadCard(String documentType, DocumentTypeConfig config) {
    final state = _uploadStates[documentType]!;

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(config.icon, size: 24, color: Colors.blue[700]),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        config.title,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        config.description,
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Upload status
            if (state.isUploaded) ...[
              _buildUploadedStatus(state),
            ] else if (state.file != null) ...[
              _buildSelectedFilePreview(documentType, state),
            ] else ...[
              _buildUploadButtons(documentType),
            ],

            // Error message
            if (state.errorMessage != null) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(color: Colors.red[300]!),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error_outline, color: Colors.red[700], size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        state.errorMessage!,
                        style: TextStyle(color: Colors.red[700], fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildUploadButtons(String documentType) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => _pickImage(documentType, ImageSource.gallery),
                icon: const Icon(Icons.photo_library),
                label: const Text('Gallery'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => _pickImage(documentType, ImageSource.camera),
                icon: const Icon(Icons.camera_alt),
                label: const Text('Camera'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: () => _pickFile(documentType),
            icon: const Icon(Icons.insert_drive_file),
            label: const Text('Choose File (PDF, DOC, etc.)'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSelectedFilePreview(String documentType, DocumentUploadState state) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.blue[50],
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.blue[200]!),
          ),
          child: Row(
            children: [
              Icon(Icons.insert_drive_file, color: Colors.blue[700]),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      state.file!.path.split('/').last,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    Text(
                      _getFileSizeString(state.file!),
                      style: const TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                  ],
                ),
              ),
              IconButton(
                onPressed: () => _removeSelectedFile(documentType),
                icon: const Icon(Icons.close),
                color: Colors.grey,
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Upload progress or upload button
        if (state.isUploading) ...[
          Column(
            children: [
              LinearProgressIndicator(
                value: state.uploadProgress,
                backgroundColor: Colors.grey[300],
                valueColor: AlwaysStoppedAnimation<Color>(Colors.blue[700]!),
              ),
              const SizedBox(height: 8),
              Text(
                'Uploading... ${(state.uploadProgress * 100).toInt()}%',
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ],
          ),
        ] else ...[
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () => _uploadDocument(documentType),
              icon: const Icon(Icons.cloud_upload),
              label: const Text('Upload Document'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue[700],
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildUploadedStatus(DocumentUploadState state) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.green[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.green[300]!),
      ),
      child: Row(
        children: [
          Icon(Icons.check_circle, color: Colors.green[700]),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Document uploaded successfully',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  'Status: ${state.documentResponse?.friendlyVerificationStatus ?? "Pending"}',
                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _pickImage(String documentType, ImageSource source) async {
    try {
      setState(() {
        _uploadStates[documentType]!.errorMessage = null;
      });

      File? file;
      if (source == ImageSource.gallery) {
        file = await _documentService.pickImageFromGallery();
      } else {
        file = await _documentService.pickImageFromCamera();
      }

      if (file != null) {
        // Validate file
        String? validationError = _documentService.validateFile(file);
        if (validationError != null) {
          setState(() {
            _uploadStates[documentType]!.errorMessage = validationError;
          });
          return;
        }

        setState(() {
          _uploadStates[documentType]!.file = file;
          _uploadStates[documentType]!.errorMessage = null;
        });
      }
    } catch (e) {
      setState(() {
        _uploadStates[documentType]!.errorMessage = e.toString();
      });
    }
  }

  Future<void> _pickFile(String documentType) async {
    try {
      setState(() {
        _uploadStates[documentType]!.errorMessage = null;
      });

      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'],
      );

      if (result != null && result.files.single.path != null) {
        File file = File(result.files.single.path!);

        // Validate file
        String? validationError = _documentService.validateFile(file);
        if (validationError != null) {
          setState(() {
            _uploadStates[documentType]!.errorMessage = validationError;
          });
          return;
        }

        setState(() {
          _uploadStates[documentType]!.file = file;
          _uploadStates[documentType]!.errorMessage = null;
        });
      }
    } catch (e) {
      setState(() {
        _uploadStates[documentType]!.errorMessage = e.toString();
      });
    }
  }

  void _removeSelectedFile(String documentType) {
    setState(() {
      _uploadStates[documentType]!.file = null;
      _uploadStates[documentType]!.errorMessage = null;
    });
  }

  Future<void> _uploadDocument(String documentType) async {
    final state = _uploadStates[documentType]!;
    if (state.file == null) return;

    setState(() {
      state.isUploading = true;
      state.uploadProgress = 0.0;
      state.errorMessage = null;
    });

    try {
      DocumentResponse response = await _documentService.uploadRegistrationDocument(
        file: state.file!,
        documentType: documentType,
        userId: widget.userId ?? 0, // Use provided userId or fallback to 0
        onProgress: (sent, total) {
          setState(() {
            state.uploadProgress = sent / total;
          });
        },
      );

      setState(() {
        state.isUploading = false;
        state.isUploaded = true;
        state.documentResponse = response;
      });

      // Show success message
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${_documentTypes[documentType]!.title} uploaded successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      setState(() {
        state.isUploading = false;
        state.errorMessage = e.toString();
      });

      // Show error message
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Upload failed: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  bool _canComplete() {
    return _uploadStates.values.every((state) => state.isUploaded);
  }

  void _completeOnboarding() {
    if (widget.onCompleted != null) {
      widget.onCompleted!();
    }
  }

  String _getFileSizeString(File file) {
    int bytes = file.lengthSync();
    if (bytes < 1024) {
      return '$bytes B';
    } else if (bytes < 1024 * 1024) {
      return '${(bytes / 1024).toStringAsFixed(1)} KB';
    } else {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    }
  }
}

class DocumentUploadState {
  File? file;
  bool isUploading = false;
  bool isUploaded = false;
  double uploadProgress = 0.0;
  String? errorMessage;
  DocumentResponse? documentResponse;
}

class DocumentTypeConfig {
  final String title;
  final String description;
  final IconData icon;

  DocumentTypeConfig({
    required this.title,
    required this.description,
    required this.icon,
  });
}

class _ProgressIndicator extends StatelessWidget {
  final int currentStep;
  final int totalSteps;

  const _ProgressIndicator({
    required this.currentStep,
    required this.totalSteps,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: List.generate(totalSteps, (index) {
        final isActive = index < currentStep;
        final isCurrent = index == currentStep - 1;

        return Expanded(
          child: Container(
            height: 4,
            margin: EdgeInsets.symmetric(horizontal: 2),
            decoration: BoxDecoration(
              color: isActive || isCurrent ? Colors.amber : Colors.grey[300],
              borderRadius: BorderRadius.circular(2),
            ),
          ),
        );
      }),
    );
  }
}