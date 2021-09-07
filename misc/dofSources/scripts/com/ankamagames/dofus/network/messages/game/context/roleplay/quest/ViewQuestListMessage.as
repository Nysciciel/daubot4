package com.ankamagames.dofus.network.messages.game.context.roleplay.quest
{
   import com.ankamagames.dofus.network.types.game.context.roleplay.quest.QuestActiveInformations;
   import com.ankamagames.jerakine.network.CustomDataWrapper;
   import com.ankamagames.jerakine.network.ICustomDataInput;
   import com.ankamagames.jerakine.network.ICustomDataOutput;
   import com.ankamagames.jerakine.network.INetworkMessage;
   import com.ankamagames.jerakine.network.utils.FuncTree;
   import flash.utils.ByteArray;
   
   public class ViewQuestListMessage extends QuestListMessage implements INetworkMessage
   {
      
      public static const protocolId:uint = 5319;
       
      
      private var _isInitialized:Boolean = false;
      
      public function ViewQuestListMessage()
      {
         super();
      }
      
      override public function get isInitialized() : Boolean
      {
         return super.isInitialized && this._isInitialized;
      }
      
      override public function getMessageId() : uint
      {
         return 5319;
      }
      
      public function initViewQuestListMessage(finishedQuestsIds:Vector.<uint> = null, finishedQuestsCounts:Vector.<uint> = null, activeQuests:Vector.<QuestActiveInformations> = null, reinitDoneQuestsIds:Vector.<uint> = null) : ViewQuestListMessage
      {
         super.initQuestListMessage(finishedQuestsIds,finishedQuestsCounts,activeQuests,reinitDoneQuestsIds);
         this._isInitialized = true;
         return this;
      }
      
      override public function reset() : void
      {
         super.reset();
         this._isInitialized = false;
      }
      
      override public function pack(output:ICustomDataOutput) : void
      {
         var data:ByteArray = new ByteArray();
         this.serialize(new CustomDataWrapper(data));
         writePacket(output,this.getMessageId(),data);
      }
      
      override public function unpack(input:ICustomDataInput, length:uint) : void
      {
         this.deserialize(input);
      }
      
      override public function unpackAsync(input:ICustomDataInput, length:uint) : FuncTree
      {
         var tree:FuncTree = new FuncTree();
         tree.setRoot(input);
         this.deserializeAsync(tree);
         return tree;
      }
      
      override public function serialize(output:ICustomDataOutput) : void
      {
         this.serializeAs_ViewQuestListMessage(output);
      }
      
      public function serializeAs_ViewQuestListMessage(output:ICustomDataOutput) : void
      {
         super.serializeAs_QuestListMessage(output);
      }
      
      override public function deserialize(input:ICustomDataInput) : void
      {
         this.deserializeAs_ViewQuestListMessage(input);
      }
      
      public function deserializeAs_ViewQuestListMessage(input:ICustomDataInput) : void
      {
         super.deserialize(input);
      }
      
      override public function deserializeAsync(tree:FuncTree) : void
      {
         this.deserializeAsyncAs_ViewQuestListMessage(tree);
      }
      
      public function deserializeAsyncAs_ViewQuestListMessage(tree:FuncTree) : void
      {
         super.deserializeAsync(tree);
      }
   }
}
