import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'payment_setup_screen.dart';

class DocumentsScreen extends StatefulWidget {
  final Map<String, String> registrationData;

  const DocumentsScreen({
    Key? key,
    required this.registrationData,
  }) : super(key: key);

  @override
  _DocumentsScreenState createState() => _DocumentsScreenState();
}

class _DocumentsScreenState extends State<DocumentsScreen> {
  final ImagePicker _picker = ImagePicker();

  File? _idDocument;
  File? _diplomaDocument;
  File? _certificateDocument;

  bool get _hasRequiredDocuments => _idDocument != null && _diplomaDocument != null;

  Future<void> _pickDocument(String documentType) async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (image != null) {
        setState(() {
          switch (documentType) {
            case 'id':
              _idDocument = File(image.path);
              break;
            case 'diploma':
              _diplomaDocument = File(image.path);
              break;
            case 'certificate':
              _certificateDocument = File(image.path);
              break;
          }
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error selecting document: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _takePhoto(String documentType) async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (image != null) {
        setState(() {
          switch (documentType) {
            case 'id':
              _idDocument = File(image.path);
              break;
            case 'diploma':
              _diplomaDocument = File(image.path);
              break;
            case 'certificate':
              _certificateDocument = File(image.path);
              break;
          }
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error taking photo: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _showDocumentOptions(String documentType, String title) {
    showModalBottomSheet(
      context: context,
      builder: (BuildContext context) {
        return SafeArea(
          child: Wrap(
            children: [
              ListTile(
                leading: Icon(Icons.photo_camera),
                title: Text('Take Photo'),
                onTap: () {
                  Navigator.pop(context);
                  _takePhoto(documentType);
                },
              ),
              ListTile(
                leading: Icon(Icons.photo_library),
                title: Text('Choose from Gallery'),
                onTap: () {
                  Navigator.pop(context);
                  _pickDocument(documentType);
                },
              ),
            ],
          ),
        );
      },
    );
  }

  void _removeDocument(String documentType) {
    setState(() {
      switch (documentType) {
        case 'id':
          _idDocument = null;
          break;
        case 'diploma':
          _diplomaDocument = null;
          break;
        case 'certificate':
          _certificateDocument = null;
          break;
      }
    });
  }

  void _nextStep() {
    if (!_hasRequiredDocuments) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Please upload all required documents'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    // Pass documents along with registration data
    final documentsData = {
      ...widget.registrationData,
      'documents': {
        'id': _idDocument?.path,
        'diploma': _diplomaDocument?.path,
        'certificate': _certificateDocument?.path,
      }
    };

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => PaymentSetupScreen(
          registrationData: documentsData,
        ),
      ),
    );
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
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Header
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
                'Step 3 of 4: Verify your identity',
                style: TextStyle(
                  fontSize: 16,
                  color: theme.colorScheme.onBackground.withOpacity(0.7),
                ),
              ),
              SizedBox(height: 24),

              // Progress indicator
              _ProgressIndicator(currentStep: 3, totalSteps: 4),
              SizedBox(height: 32),

              // Instructions
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.blue[200]!),
                ),
                child: Column(
                  children: [
                    Icon(Icons.info_outline, color: Colors.blue[700], size: 24),
                    SizedBox(height: 8),
                    Text(
                      'Document Guidelines',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        color: Colors.blue[700],
                      ),
                    ),
                    SizedBox(height: 8),
                    Text(
                      '• Ensure documents are clear and readable\n'
                      '• All four corners should be visible\n'
                      '• Good lighting with no shadows\n'
                      '• File size should be under 10MB',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.blue[700],
                      ),
                    ),
                  ],
                ),
              ),
              SizedBox(height: 32),

              // Document upload cards
              _DocumentCard(
                title: 'Photo ID *',
                subtitle: 'Driver\'s license, passport, or state ID',
                file: _idDocument,
                isRequired: true,
                onTap: () => _showDocumentOptions('id', 'Photo ID'),
                onRemove: () => _removeDocument('id'),
              ),
              SizedBox(height: 16),

              _DocumentCard(
                title: 'High School Diploma/GED *',
                subtitle: 'Educational requirement verification',
                file: _diplomaDocument,
                isRequired: true,
                onTap: () => _showDocumentOptions('diploma', 'Diploma/GED'),
                onRemove: () => _removeDocument('diploma'),
              ),
              SizedBox(height: 16),

              _DocumentCard(
                title: 'Additional Certificates',
                subtitle: 'Any relevant certifications (optional)',
                file: _certificateDocument,
                isRequired: false,
                onTap: () => _showDocumentOptions('certificate', 'Certificates'),
                onRemove: () => _removeDocument('certificate'),
              ),
              SizedBox(height: 32),

              // Note about verification
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.amber[50],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.amber[200]!),
                ),
                child: Row(
                  children: [
                    Icon(Icons.schedule, color: Colors.amber[700], size: 20),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Documents will be reviewed within 1-2 business days. You\'ll be notified via email once verified.',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.amber[700],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              SizedBox(height: 32),

              // Next button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _hasRequiredDocuments ? _nextStep : null,
                  style: ElevatedButton.styleFrom(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: _hasRequiredDocuments ? Colors.amber : Colors.grey,
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: Text(
                    'Next Step',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                ),
              ),
              SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }
}

class _DocumentCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final File? file;
  final bool isRequired;
  final VoidCallback onTap;
  final VoidCallback onRemove;

  const _DocumentCard({
    required this.title,
    required this.subtitle,
    required this.file,
    required this.isRequired,
    required this.onTap,
    required this.onRemove,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final hasFile = file != null;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: hasFile ? Colors.green : (isRequired ? Colors.red[300]! : Colors.grey[300]!),
          width: hasFile ? 2 : 1,
        ),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          title,
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: theme.colorScheme.onSurface,
                          ),
                        ),
                        SizedBox(height: 4),
                        Text(
                          subtitle,
                          style: TextStyle(
                            fontSize: 14,
                            color: theme.colorScheme.onSurface.withOpacity(0.7),
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (hasFile)
                    Row(
                      children: [
                        Icon(Icons.check_circle, color: Colors.green, size: 24),
                        SizedBox(width: 8),
                        IconButton(
                          onPressed: onRemove,
                          icon: Icon(Icons.close, color: Colors.red),
                          constraints: BoxConstraints(),
                          padding: EdgeInsets.zero,
                        ),
                      ],
                    )
                  else
                    Icon(
                      Icons.upload_file,
                      color: theme.colorScheme.onSurface.withOpacity(0.5),
                      size: 24,
                    ),
                ],
              ),
              if (hasFile) ...[
                SizedBox(height: 12),
                Container(
                  height: 100,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8),
                    image: DecorationImage(
                      image: FileImage(file!),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  'Document uploaded successfully',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.green,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ] else ...[
                SizedBox(height: 12),
                Text(
                  'Tap to upload ${isRequired ? '(Required)' : '(Optional)'}',
                  style: TextStyle(
                    fontSize: 14,
                    color: isRequired ? Colors.red[600] : theme.colorScheme.onSurface.withOpacity(0.6),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
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