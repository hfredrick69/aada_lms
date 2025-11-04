import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'registration_confirm_screen.dart';

class PersonalInfoScreen extends StatefulWidget {
  final String email;
  final String password;

  const PersonalInfoScreen({
    Key? key,
    required this.email,
    required this.password,
  }) : super(key: key);

  @override
  _PersonalInfoScreenState createState() => _PersonalInfoScreenState();
}

class _PersonalInfoScreenState extends State<PersonalInfoScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _addressLine1Controller = TextEditingController();
  final _addressLine2Controller = TextEditingController();
  final _cityController = TextEditingController();
  final _zipCodeController = TextEditingController();
  final _emergencyContactNameController = TextEditingController();
  final _emergencyContactPhoneController = TextEditingController();

  String _selectedState = '';
  final List<String> _states = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
  ];

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _phoneController.dispose();
    _addressLine1Controller.dispose();
    _addressLine2Controller.dispose();
    _cityController.dispose();
    _zipCodeController.dispose();
    _emergencyContactNameController.dispose();
    _emergencyContactPhoneController.dispose();
    super.dispose();
  }

  void _nextStep() {
    if (_formKey.currentState!.validate()) {
      // Collect registration data
      final registrationData = {
        'email': widget.email,
        'password': widget.password,
        'first_name': _firstNameController.text.trim(),
        'last_name': _lastNameController.text.trim(),
        'phone': _phoneController.text.trim(),
        'address_line1': _addressLine1Controller.text.trim(),
        'address_line2': _addressLine2Controller.text.trim(),
        'city': _cityController.text.trim(),
        'state': _selectedState,
        'zip_code': _zipCodeController.text.trim(),
        'emergency_contact_name': _emergencyContactNameController.text.trim(),
        'emergency_contact_phone': _emergencyContactPhoneController.text.trim(),
      };

      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => RegistrationConfirmScreen(
            registrationData: registrationData,
          ),
        ),
      );
    }
  }

  String? _validateRequired(String? value, String fieldName) {
    if (value == null || value.trim().isEmpty) {
      return 'Please enter your $fieldName';
    }
    return null;
  }

  String? _validatePhone(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter your phone number';
    }
    final phoneRegex = RegExp(r'^\(\d{3}\) \d{3}-\d{4}$');
    if (!phoneRegex.hasMatch(value)) {
      return 'Please enter a valid phone number';
    }
    return null;
  }

  String? _validateZipCode(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter your ZIP code';
    }
    final zipRegex = RegExp(r'^\d{5}(-\d{4})?$');
    if (!zipRegex.hasMatch(value)) {
      return 'Please enter a valid ZIP code';
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.colorScheme.background,
      appBar: AppBar(
        title: Text('Personal Information'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: theme.colorScheme.onBackground,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Header
                Text(
                  'Personal Information',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.amber,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  'Step 2 of 4: Tell us about yourself',
                  style: TextStyle(
                    fontSize: 16,
                    color: theme.colorScheme.onBackground.withOpacity(0.7),
                  ),
                ),
                SizedBox(height: 24),

                // Progress indicator
                _ProgressIndicator(currentStep: 2, totalSteps: 4),
                SizedBox(height: 32),

                // Name fields
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _firstNameController,
                        validator: (value) => _validateRequired(value, 'first name'),
                        decoration: InputDecoration(
                          labelText: 'First Name *',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                      ),
                    ),
                    SizedBox(width: 16),
                    Expanded(
                      child: TextFormField(
                        controller: _lastNameController,
                        validator: (value) => _validateRequired(value, 'last name'),
                        decoration: InputDecoration(
                          labelText: 'Last Name *',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 16),

                // Phone field
                TextFormField(
                  controller: _phoneController,
                  keyboardType: TextInputType.phone,
                  validator: _validatePhone,
                  inputFormatters: [_PhoneInputFormatter()],
                  decoration: InputDecoration(
                    labelText: 'Phone Number *',
                    hintText: '(555) 123-4567',
                    prefixIcon: Icon(Icons.phone_outlined),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
                SizedBox(height: 24),

                // Address section
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'Address',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: theme.colorScheme.onBackground,
                    ),
                  ),
                ),
                SizedBox(height: 16),

                TextFormField(
                  controller: _addressLine1Controller,
                  validator: (value) => _validateRequired(value, 'address'),
                  decoration: InputDecoration(
                    labelText: 'Address Line 1 *',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
                SizedBox(height: 16),

                TextFormField(
                  controller: _addressLine2Controller,
                  decoration: InputDecoration(
                    labelText: 'Address Line 2 (Optional)',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
                SizedBox(height: 16),

                Row(
                  children: [
                    Expanded(
                      flex: 2,
                      child: TextFormField(
                        controller: _cityController,
                        validator: (value) => _validateRequired(value, 'city'),
                        decoration: InputDecoration(
                          labelText: 'City *',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                      ),
                    ),
                    SizedBox(width: 16),
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        value: _selectedState.isEmpty ? null : _selectedState,
                        validator: (value) => value == null ? 'Select state' : null,
                        decoration: InputDecoration(
                          labelText: 'State *',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        items: _states.map((state) {
                          return DropdownMenuItem(
                            value: state,
                            child: Text(state),
                          );
                        }).toList(),
                        onChanged: (value) {
                          setState(() {
                            _selectedState = value ?? '';
                          });
                        },
                      ),
                    ),
                    SizedBox(width: 16),
                    Expanded(
                      child: TextFormField(
                        controller: _zipCodeController,
                        keyboardType: TextInputType.number,
                        validator: _validateZipCode,
                        decoration: InputDecoration(
                          labelText: 'ZIP *',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 24),

                // Emergency contact section
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'Emergency Contact',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: theme.colorScheme.onBackground,
                    ),
                  ),
                ),
                SizedBox(height: 16),

                TextFormField(
                  controller: _emergencyContactNameController,
                  validator: (value) => _validateRequired(value, 'emergency contact name'),
                  decoration: InputDecoration(
                    labelText: 'Emergency Contact Name *',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
                SizedBox(height: 16),

                TextFormField(
                  controller: _emergencyContactPhoneController,
                  keyboardType: TextInputType.phone,
                  validator: _validatePhone,
                  inputFormatters: [_PhoneInputFormatter()],
                  decoration: InputDecoration(
                    labelText: 'Emergency Contact Phone *',
                    hintText: '(555) 123-4567',
                    prefixIcon: Icon(Icons.phone_outlined),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
                SizedBox(height: 32),

                // Next button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _nextStep,
                    style: ElevatedButton.styleFrom(
                      padding: EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: Colors.amber,
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

class _PhoneInputFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    final newText = newValue.text;
    if (newText.length > 14) return oldValue;

    final digitsOnly = newText.replaceAll(RegExp(r'[^\d]'), '');
    String formatted = '';

    if (digitsOnly.isNotEmpty) {
      if (digitsOnly.length <= 3) {
        formatted = '(${digitsOnly}';
      } else if (digitsOnly.length <= 6) {
        formatted = '(${digitsOnly.substring(0, 3)}) ${digitsOnly.substring(3)}';
      } else {
        formatted = '(${digitsOnly.substring(0, 3)}) ${digitsOnly.substring(3, 6)}-${digitsOnly.substring(6, digitsOnly.length > 10 ? 10 : digitsOnly.length)}';
      }
    }

    return TextEditingValue(
      text: formatted,
      selection: TextSelection.collapsed(offset: formatted.length),
    );
  }
}