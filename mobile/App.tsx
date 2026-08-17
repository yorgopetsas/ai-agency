import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { ThemeProvider, useTheme } from './src/theme/ThemeContext';
import AppNavigator from './src/navigation/AppNavigator';
import { api } from './src/services/api';

function AppContent() {
  const { loading } = useTheme();

  if (loading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#6366f1" />
      </View>
    );
  }

  return <AppNavigator />;
}

export default function App() {
  return (
    <ThemeProvider>
      <StatusBar style="auto" />
      <AppContent />
    </ThemeProvider>
  );
}

const styles = StyleSheet.create({
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f8fafc' },
});
