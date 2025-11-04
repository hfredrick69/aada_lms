import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'quizzes_screen.dart';
import 'job_board_screen.dart';
import 'my_tuition_screen.dart';
import 'login_screen.dart';
import '../providers/auth_provider.dart';
import '../services/document_service.dart';
import '../utils/secure_storage.dart';

class DashboardScreen extends StatefulWidget {
  final Map<String, dynamic> student;
  DashboardScreen({required this.student});

  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final DocumentService _documentService = DocumentService();
  List<DocumentResponse>? _documents;
  bool _isLoadingDocuments = true;
  String? _documentError;

  @override
  void initState() {
    super.initState();
    _loadDocuments();
  }

  Future<void> _loadDocuments() async {
    try {
      // Set auth token from storage
      final token = await SecureStorage.getAccessToken();
      if (token != null) {
        _documentService.setAuthToken(token);
      }

      final documents = await _documentService.getUserDocuments();
      setState(() {
        _documents = documents;
        _isLoadingDocuments = false;
      });
    } catch (e) {
      setState(() {
        _documentError = e.toString();
        _isLoadingDocuments = false;
      });
    }
  }

  void logout(BuildContext context) {
    final authProvider = context.read<AuthProvider>();
    authProvider.logout();
  }

  void navigateTo(BuildContext context, Widget screen) {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => screen),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text("Dashboard"),
        actions: [
          IconButton(
            icon: Icon(Icons.logout),
            onPressed: () => logout(context),
          )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Welcome, ${widget.student['name']}!",
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.onBackground,
              ),
            ),
            SizedBox(height: 24),

            // Documents Section
            Text(
              "My Documents",
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: theme.colorScheme.onBackground,
              ),
            ),
            SizedBox(height: 12),

            if (_isLoadingDocuments)
              Center(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: CircularProgressIndicator(),
                ),
              )
            else if (_documentError != null)
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.red[200]!),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error_outline, color: Colors.red[700]),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Error loading documents: $_documentError',
                        style: TextStyle(color: Colors.red[700]),
                      ),
                    ),
                  ],
                ),
              )
            else if (_documents == null || _documents!.isEmpty)
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey[300]!),
                ),
                child: Row(
                  children: [
                    Icon(Icons.folder_open, color: Colors.grey[600]),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'No documents uploaded yet',
                        style: TextStyle(color: Colors.grey[700]),
                      ),
                    ),
                  ],
                ),
              )
            else
              ListView.builder(
                shrinkWrap: true,
                physics: NeverScrollableScrollPhysics(),
                itemCount: _documents!.length,
                itemBuilder: (context, index) {
                  final doc = _documents![index];
                  return _DocumentCard(document: doc);
                },
              ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 0,
        selectedItemColor: Colors.black,
        unselectedItemColor: Colors.grey,
        onTap: (index) {
          if (index == 1) navigateTo(context, QuizzesScreen(student: widget.student));
          if (index == 2) navigateTo(context, JobBoardScreen(student: widget.student));
          if (index == 3) navigateTo(context, MyTuitionScreen(student: widget.student));
        },
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: "Dashboard"),
          BottomNavigationBarItem(icon: Icon(Icons.quiz), label: "Quizzes"),
          BottomNavigationBarItem(icon: Icon(Icons.work), label: "Job Board"),
          BottomNavigationBarItem(icon: Icon(Icons.attach_money), label: "My Tuition"),
        ],
      ),
    );
  }
}

class _DocumentCard extends StatelessWidget {
  final DocumentResponse document;

  const _DocumentCard({required this.document});

  Color _getStatusColor() {
    switch (document.verificationStatus) {
      case 'approved':
        return Colors.green;
      case 'rejected':
        return Colors.red;
      case 'pending':
      default:
        return Colors.orange;
    }
  }

  IconData _getStatusIcon() {
    switch (document.verificationStatus) {
      case 'approved':
        return Icons.check_circle;
      case 'rejected':
        return Icons.cancel;
      case 'pending':
      default:
        return Icons.schedule;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final statusColor = _getStatusColor();

    return Card(
      margin: EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: statusColor.withOpacity(0.3), width: 1),
      ),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.description, color: statusColor, size: 24),
                SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        document.friendlyDocumentType,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: theme.colorScheme.onSurface,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        document.fileName,
                        style: TextStyle(
                          fontSize: 14,
                          color: theme.colorScheme.onSurface.withOpacity(0.7),
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                Icon(_getStatusIcon(), color: statusColor, size: 24),
              ],
            ),
            SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Row(
                    children: [
                      Icon(Icons.calendar_today, size: 14, color: Colors.grey[600]),
                      SizedBox(width: 4),
                      Text(
                        'Uploaded: ${document.uploadedAt.toString().split(' ')[0]}',
                        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    document.friendlyVerificationStatus,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: statusColor,
                    ),
                  ),
                ),
              ],
            ),
            if (document.verificationNotes != null) ...[
              SizedBox(height: 12),
              Container(
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.note, size: 16, color: Colors.grey[700]),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        document.verificationNotes!,
                        style: TextStyle(fontSize: 12, color: Colors.grey[700]),
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
}
