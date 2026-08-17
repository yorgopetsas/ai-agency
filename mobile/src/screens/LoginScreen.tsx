import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, KeyboardAvoidingView, Platform, StyleSheet } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { api } from '../services/api';
import { useNavigation } from '@react-navigation/native';

export default function LoginScreen() {
  const { theme, config } = useTheme();
  const navigation = useNavigation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please enter email and password');
      return;
    }
    setLoading(true);
    try {
      await api.login(email, password);
      navigation.reset({ index: 0, routes: [{ name: 'Main' as never }] });
    } catch (err: any) {
      Alert.alert('Login Failed', err.response?.data?.error || 'Invalid credentials');
    }
    setLoading(false);
  };

  const styles = makeStyles(theme);

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <View style={styles.inner}>
        <View style={styles.logoContainer}>
          <Text style={styles.logoText}>{config.companyName}</Text>
          <Text style={styles.subtitle}>Sign in to your account</Text>
        </View>

        <View style={styles.form}>
          <Text style={styles.label}>Email</Text>
          <TextInput
            style={styles.input}
            value={email}
            onChangeText={setEmail}
            placeholder="you@example.com"
            keyboardType="email-address"
            autoCapitalize="none"
            autoCorrect={false}
          />

          <Text style={styles.label}>Password</Text>
          <TextInput
            style={styles.input}
            value={password}
            onChangeText={setPassword}
            placeholder="Your password"
            secureTextEntry
          />

          <TouchableOpacity style={styles.loginButton} onPress={handleLogin} disabled={loading}>
            <Text style={styles.loginButtonText}>{loading ? 'Signing in...' : 'Sign In'}</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.footer}>Powered by AI Agency Platform</Text>
      </View>
    </KeyboardAvoidingView>
  );
}

function makeStyles(theme: any) {
  return StyleSheet.create({
    container: { flex: 1, backgroundColor: theme.colors.background },
    inner: { flex: 1, justifyContent: 'center', padding: theme.spacing.xl },
    logoContainer: { alignItems: 'center', marginBottom: 40 },
    logoText: { fontSize: 32, fontWeight: 'bold', color: theme.colors.primary },
    subtitle: { fontSize: 16, color: theme.colors.textSecondary, marginTop: 8 },
    form: { marginBottom: 30 },
    label: { fontSize: 14, color: theme.colors.textSecondary, marginBottom: 6 },
    input: { backgroundColor: theme.colors.card, borderWidth: 1, borderColor: theme.colors.border, borderRadius: theme.borderRadius, padding: 16, fontSize: 16, color: theme.colors.text, marginBottom: 16 },
    loginButton: { backgroundColor: theme.colors.primary, padding: 16, borderRadius: theme.borderRadius, alignItems: 'center', marginTop: 8 },
    loginButtonText: { color: '#fff', fontSize: 18, fontWeight: '600' },
    footer: { textAlign: 'center', color: theme.colors.textMuted, fontSize: 12 },
  });
}
