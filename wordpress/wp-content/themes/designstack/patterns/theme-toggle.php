<?php
/**
 * Title: Переключатель темы
 * Slug: designstack/theme-toggle
 * Categories: designstack
 * Inserter: no
 *
 * Подпись одна — «Тёмная тема»; включена ли тема, сообщает aria-pressed (docs/VOICE.md). Скрипт — assets/js/theme-toggle.js.
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<div class="ds-row">
	<button type="button" class="ds-button ds-button--icon ds-theme-toggle" aria-pressed="false"><?php echo designstack_icon( 'moon', '', 'ds-theme-toggle__moon' ); ?><?php echo designstack_icon( 'sun', '', 'ds-theme-toggle__sun' ); ?><span class="screen-reader-text">Тёмная тема</span></button>
	<button type="button" class="ds-button ds-button--icon ds-theme-toggle is-pressed" aria-pressed="true"><?php echo designstack_icon( 'moon', '', 'ds-theme-toggle__moon' ); ?><?php echo designstack_icon( 'sun', '', 'ds-theme-toggle__sun' ); ?><span class="screen-reader-text">Тёмная тема</span></button>
</div>
<!-- /wp:html -->
