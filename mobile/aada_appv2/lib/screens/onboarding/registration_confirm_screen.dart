import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import 'document_upload_step.dart';
import 'payment_setup_screen.dart';

class RegistrationConfirmScreen extends StatefulWidget {
  final Map<String, dynamic> registrationData;

  const RegistrationConfirmScreen({
    Key? key,
    required this.registrationData,
  }) : super(key: key);

  @override
  _RegistrationConfirmScreenState createState() => _RegistrationConfirmScreenState();
}

class _RegistrationConfirmScreenState extends State<RegistrationConfirmScreen> {
  bool _isLoading = false;
  bool _agreedToTerms = false;

  Future<void> _completeRegistration() async {
    if (!_agreedToTerms) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Please agree to the terms and conditions'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final authProvider = context.read<AuthProvider>();

      // Register the user
      final registrationResult = await authProvider.register(
        email: widget.registrationData['email'],
        password: widget.registrationData['password'],
        firstName: widget.registrationData['first_name'],
        lastName: widget.registrationData['last_name'],
      );

      if (registrationResult != null) {
        // Navigate to document upload with the user ID
        _navigateToDocumentUpload(registrationResult['id']);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authProvider.errorMessage ?? 'Registration failed'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _navigateToDocumentUpload(int userId) {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => DocumentUploadStep(
          userId: userId,
          onCompleted: () {
            // Navigate to payment setup after document upload
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(
                builder: (context) => PaymentSetupScreen(
                  registrationData: widget.registrationData,
                ),
              ),
            );
          },
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
        title: Text('Confirm Registration'),
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
                'Confirm Registration',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.amber,
                ),
              ),
              SizedBox(height: 8),
              Text(
                'Step 3 of 4: Review and confirm your registration',
                style: TextStyle(
                  fontSize: 16,
                  color: theme.colorScheme.onBackground.withOpacity(0.7),
                ),
              ),
              SizedBox(height: 24),

              // Progress indicator
              _ProgressIndicator(currentStep: 3, totalSteps: 4),
              SizedBox(height: 32),

              // Registration summary
              Card(
                elevation: 2,
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Registration Summary',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 16),
                      _buildSummaryRow('Email', widget.registrationData['email']),
                      _buildSummaryRow('Name', '${widget.registrationData['first_name']} ${widget.registrationData['last_name']}'),
                      _buildSummaryRow('Phone', widget.registrationData['phone'] ?? 'Not provided'),
                      _buildSummaryRow('City', widget.registrationData['city']),
                      _buildSummaryRow('State', widget.registrationData['state']),
                    ],
                  ),
                ),
              ),
              SizedBox(height: 24),

              // Terms and conditions
              Row(
                children: [
                  Checkbox(
                    value: _agreedToTerms,
                    onChanged: (value) {
                      setState(() {
                        _agreedToTerms = value ?? false;
                      });
                    },
                    activeColor: Colors.amber,
                  ),
                  Expanded(
                    child: GestureDetector(
                      onTap: () {
                        setState(() {
                          _agreedToTerms = !_agreedToTerms;
                        });
                      },
                      child: Text(
                        'I agree to the Terms of Service and Privacy Policy',
                        style: TextStyle(fontSize: 14),
                      ),
                    ),
                  ),
                ],
              ),
              SizedBox(height: 24),

              // Complete registration button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _completeRegistration,
                  style: ElevatedButton.styleFrom(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: Colors.amber,
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _isLoading
                      ? CircularProgressIndicator(color: Colors.black)
                      : Text(
                          'Complete Registration',
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

  Widget _buildSummaryRow(String label, String value) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: TextStyle(
                fontWeight: FontWeight.w500,
                color: Colors.grey[600],
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(fontWeight: FontWeight.w400),
            ),
          ),
        ],
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