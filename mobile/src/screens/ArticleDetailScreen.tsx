import React from 'react';
import { View, Text, ScrollView, Image, TouchableOpacity, Linking, StyleSheet } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { useRoute } from '@react-navigation/native';
import { Article } from '../services/api';

export default function ArticleDetailScreen() {
  const { theme } = useTheme();
  const route = useRoute();
  const article = (route.params as any)?.article as Article;

  if (!article) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <Text>Article not found</Text>
      </View>
    );
  }

  const styles = makeStyles(theme);

  return (
    <ScrollView style={styles.container}>
      {article.image_url ? (
        <Image source={{ uri: article.image_url }} style={styles.image} />
      ) : null}

      <View style={styles.body}>
        <Text style={styles.title}>{article.headline}</Text>

        <View style={styles.meta}>
          <Text style={styles.date}>{article.date_formatted}</Text>
          {article.provider ? <Text style={styles.provider}>by {article.provider}</Text> : null}
          {article.rating ? <Text style={styles.rating}>Score: {article.rating.total}/100</Text> : null}
        </View>

        <Text style={styles.overview}>{article.overview}</Text>

        {article.paragraphs?.map((para: string, i: number) => (
          <Text key={i} style={styles.paragraph}>{para}</Text>
        ))}

        {article.source_url ? (
          <TouchableOpacity style={styles.sourceButton} onPress={() => Linking.openURL(article.source_url)}>
            <Text style={styles.sourceButtonText}>Read Original Source</Text>
          </TouchableOpacity>
        ) : null}
      </View>
    </ScrollView>
  );
}

function makeStyles(theme: any) {
  return StyleSheet.create({
    container: { flex: 1, backgroundColor: theme.colors.background },
    image: { width: '100%', height: 250 },
    body: { padding: theme.spacing.lg },
    title: { fontSize: 24, fontWeight: 'bold', color: theme.colors.text, marginBottom: 12, lineHeight: 32 },
    meta: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginBottom: 16 },
    date: { fontSize: 13, color: theme.colors.textMuted },
    provider: { fontSize: 13, color: theme.colors.primary },
    rating: { fontSize: 13, color: theme.colors.success },
    overview: { fontSize: 16, color: theme.colors.textSecondary, fontStyle: 'italic', marginBottom: 20, lineHeight: 24 },
    paragraph: { fontSize: 16, color: theme.colors.text, lineHeight: 26, marginBottom: 14 },
    sourceButton: { backgroundColor: theme.colors.primary, padding: 16, borderRadius: theme.borderRadius, alignItems: 'center', marginTop: 20, marginBottom: 40 },
    sourceButtonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  });
}
