<?php
/**
 * Title: Входы в разделы
 * Slug: designstack/entry-tiles
 * Categories: designstack
 *
 * Четыре входа в первом экране главной (US-24) и на странице 404. До 600 строка под названием не выводится.
 *
 * @package designstack
 */

$ds_entries = array(
	array( 'Инструменты', '/tools/', 'Редакторы, прототипы, тесты' ),
	array( 'Учёба', '/learn/', 'Курсы, книги, статьи, видео' ),
	array( 'Ассеты', '/assets/', 'UI-киты, шрифты, иконки, мокапы' ),
	array( 'Сообщества', '/community/', 'Каналы, чаты, вакансии' ),
);

?>
<!-- wp:html -->
<ul class="ds-entries">
	<?php foreach ( $ds_entries as $ds_entry ) : ?>
	<li><a class="ds-entry" href="<?php echo esc_url( $ds_entry[1] ); ?>"><span class="ds-entry__title"><?php echo esc_html( $ds_entry[0] ); ?></span><span class="ds-entry__note"><?php echo esc_html( $ds_entry[2] ); ?></span></a></li>
	<?php endforeach; ?>
</ul>
<!-- /wp:html -->
