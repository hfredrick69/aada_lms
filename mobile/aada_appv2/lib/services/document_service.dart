import 'dart:io';
import 'package:dio/dio.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path/path.dart' as path;
import 'package:mime/mime.dart';
import '../config/api_config.dart';

class DocumentService {
  final Dio _dio = Dio();
  final ImagePicker _picker = ImagePicker();

  // Use configuration from ApiConfig
  static const int maxFileSize = ApiConfig.maxFileSize;

  // Use configuration from ApiConfig
  static const Set<String> allowedExtensions = ApiConfig.allowedExtensions;

  // Document types mapping from UI to backend - simplified to transcripts only
  static const Map<String, String> documentTypeMapping = {
    'transcript': 'transcript',
  };

  DocumentService() {
    _dio.options.baseUrl = ApiConfig.baseUrl;
    _dio.options.connectTimeout = ApiConfig.connectTimeout;
    _dio.options.receiveTimeout = ApiConfig.receiveTimeout;
  }

  /// Set authorization token for authenticated requests
  void setAuthToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  /// Validate file before upload
  String? validateFile(File file) {
    // Check file exists
    if (!file.existsSync()) {
      return 'File does not exist';
    }

    // Check file size
    int fileSize = file.lengthSync();
    if (fileSize > maxFileSize) {
      return 'File size exceeds 10MB limit';
    }

    // Check file extension
    String fileName = path.basename(file.path);
    String extension = path.extension(fileName).toLowerCase();
    if (!allowedExtensions.contains(extension)) {
      return 'File type not allowed. Supported: ${allowedExtensions.join(', ')}';
    }

    return null; // File is valid
  }

  /// Pick image from gallery
  Future<File?> pickImageFromGallery() async {
    try {
      final XFile? pickedFile = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (pickedFile != null) {
        return File(pickedFile.path);
      }
      return null;
    } catch (e) {
      throw Exception('Failed to pick image from gallery: $e');
    }
  }

  /// Pick image from camera
  Future<File?> pickImageFromCamera() async {
    try {
      final XFile? pickedFile = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (pickedFile != null) {
        return File(pickedFile.path);
      }
      return null;
    } catch (e) {
      throw Exception('Failed to take photo: $e');
    }
  }

  /// Upload document during registration (no authentication required)
  Future<DocumentResponse> uploadRegistrationDocument({
    required File file,
    required String documentType,
    int userId = 0,
    Function(int, int)? onProgress,
  }) async {
    try {
      // Validate file first
      String? validationError = validateFile(file);
      if (validationError != null) {
        throw Exception(validationError);
      }

      // Map document type to backend format
      String backendDocumentType = documentTypeMapping[documentType] ?? documentType;

      // Get file info
      String fileName = path.basename(file.path);
      String? mimeType = lookupMimeType(file.path);

      // Create multipart form data
      FormData formData = FormData.fromMap({
        'document_type': backendDocumentType,
        'user_id': userId,
        'file': await MultipartFile.fromFile(
          file.path,
          filename: fileName,
          contentType: mimeType != null ? DioMediaType.parse(mimeType) : null,
        ),
      });

      // Upload with progress tracking (no auth required)
      Response response = await _dio.post(
        ApiConfig.documentsUploadRegistration,
        data: formData,
        onSendProgress: onProgress,
      );

      if (response.statusCode == 200) {
        return DocumentResponse.fromJson(response.data);
      } else {
        throw Exception('Upload failed with status: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data['detail'] != null) {
        throw Exception(e.response!.data['detail']);
      }
      throw Exception('Upload failed: ${e.message}');
    } catch (e) {
      throw Exception('Upload failed: $e');
    }
  }

  /// Upload document to backend (authenticated users)
  Future<DocumentResponse> uploadDocument({
    required File file,
    required String documentType,
    Function(int, int)? onProgress,
  }) async {
    try {
      // Validate file first
      String? validationError = validateFile(file);
      if (validationError != null) {
        throw Exception(validationError);
      }

      // Map document type to backend format
      String backendDocumentType = documentTypeMapping[documentType] ?? documentType;

      // Get file info
      String fileName = path.basename(file.path);
      String? mimeType = lookupMimeType(file.path);

      // Create multipart form data
      FormData formData = FormData.fromMap({
        'document_type': backendDocumentType,
        'file': await MultipartFile.fromFile(
          file.path,
          filename: fileName,
          contentType: mimeType != null ? DioMediaType.parse(mimeType) : null,
        ),
      });

      // Upload with progress tracking (requires auth)
      Response response = await _dio.post(
        ApiConfig.documentsUpload,
        data: formData,
        onSendProgress: onProgress,
      );

      if (response.statusCode == 200) {
        return DocumentResponse.fromJson(response.data);
      } else {
        throw Exception('Upload failed with status: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data['detail'] != null) {
        throw Exception(e.response!.data['detail']);
      }
      throw Exception('Upload failed: ${e.message}');
    } catch (e) {
      throw Exception('Upload failed: $e');
    }
  }

  /// Get list of user documents
  Future<List<DocumentResponse>> getUserDocuments() async {
    try {
      Response response = await _dio.get(ApiConfig.documentsList);

      if (response.statusCode == 200) {
        List<dynamic> documentsJson = response.data;
        return documentsJson
            .map((doc) => DocumentResponse.fromJson(doc))
            .toList();
      } else {
        throw Exception('Failed to fetch documents');
      }
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data['detail'] != null) {
        throw Exception(e.response!.data['detail']);
      }
      throw Exception('Failed to fetch documents: ${e.message}');
    } catch (e) {
      throw Exception('Failed to fetch documents: $e');
    }
  }

  /// Get specific document by ID
  Future<DocumentResponse> getDocument(int documentId) async {
    try {
      Response response = await _dio.get('${ApiConfig.documentsGet}/$documentId');

      if (response.statusCode == 200) {
        return DocumentResponse.fromJson(response.data);
      } else {
        throw Exception('Failed to fetch document');
      }
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data['detail'] != null) {
        throw Exception(e.response!.data['detail']);
      }
      throw Exception('Failed to fetch document: ${e.message}');
    } catch (e) {
      throw Exception('Failed to fetch document: $e');
    }
  }

  /// Delete document
  Future<void> deleteDocument(int documentId) async {
    try {
      Response response = await _dio.delete('${ApiConfig.documentsDelete}/$documentId');

      if (response.statusCode != 200) {
        throw Exception('Failed to delete document');
      }
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data['detail'] != null) {
        throw Exception(e.response!.data['detail']);
      }
      throw Exception('Failed to delete document: ${e.message}');
    } catch (e) {
      throw Exception('Failed to delete document: $e');
    }
  }
}

/// Document response model matching backend structure
class DocumentResponse {
  final int id;
  final String documentType;
  final String fileName;
  final String fileUrl;
  final int fileSize;
  final String verificationStatus;
  final String? verificationNotes;
  final DateTime uploadedAt;
  final DateTime? verifiedAt;

  DocumentResponse({
    required this.id,
    required this.documentType,
    required this.fileName,
    required this.fileUrl,
    required this.fileSize,
    required this.verificationStatus,
    this.verificationNotes,
    required this.uploadedAt,
    this.verifiedAt,
  });

  factory DocumentResponse.fromJson(Map<String, dynamic> json) {
    return DocumentResponse(
      id: json['id'],
      documentType: json['document_type'],
      fileName: json['file_name'],
      fileUrl: json['file_url'],
      fileSize: json['file_size'],
      verificationStatus: json['verification_status'],
      verificationNotes: json['verification_notes'],
      uploadedAt: DateTime.parse(json['uploaded_at']),
      verifiedAt: json['verified_at'] != null
          ? DateTime.parse(json['verified_at'])
          : null,
    );
  }

  /// Get user-friendly document type name
  String get friendlyDocumentType {
    switch (documentType) {
      case 'transcript':
        return 'Academic Transcript';
      default:
        return documentType;
    }
  }

  /// Get user-friendly verification status
  String get friendlyVerificationStatus {
    switch (verificationStatus) {
      case 'pending':
        return 'Pending Review';
      case 'approved':
        return 'Approved';
      case 'rejected':
        return 'Rejected';
      default:
        return verificationStatus;
    }
  }

  /// Get file size in human readable format
  String get formattedFileSize {
    if (fileSize < 1024) {
      return '$fileSize B';
    } else if (fileSize < 1024 * 1024) {
      return '${(fileSize / 1024).toStringAsFixed(1)} KB';
    } else {
      return '${(fileSize / (1024 * 1024)).toStringAsFixed(1)} MB';
    }
  }
}