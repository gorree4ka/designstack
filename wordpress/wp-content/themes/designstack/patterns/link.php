<?php
/**
 * Title: Ссылки: в тексте, отдельная, наружу
 * Slug: designstack/link
 * Categories: designstack
 * Inserter: no
 *
 * Ссылка отличается от текста подчёркиванием (D50); наружу — с иконкой и скрытой подписью про новую вкладку.
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<div class="ds-row">
	<span>Список тем стоит в <a class="ds-link" href="#">подвале</a> каждой страницы.</span>
	<a class="ds-link ds-link--standalone" href="#">Все подборки<?php echo designstack_icon( 'chevron-right' ); ?></a>
	<a class="ds-link ds-link--external" href="#" target="_blank" rel="noopener">help.figma.com<?php echo designstack_icon( 'external-link' ); ?><span class="screen-reader-text">откроется в новой вкладке</span></a>
</div>
<!-- /wp:html -->
